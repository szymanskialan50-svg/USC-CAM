import AVFoundation
import UIKit
import Network

@objc(CameraManager)
class CameraManager: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    private let captureSession = AVCaptureSession()
    private var listener: NWListener?
    private var activeConnection: NWConnection?

    override init() {
        super.init()
        configureBackgroundExecution()
        setupHighResCamera()
        startUSBListener()
    }

    private func configureBackgroundExecution() {
        // Keeps frame capture pipeline alive when user minimizes the app or locks the screen
        let audioSession = AVAudioSession.sharedInstance()
        do {
            try audioSession.setCategory(.playAndRecord, mode: .default, options: [.mixWithOthers, .allowBluetooth])
            try audioSession.setActive(true)
        } catch {
            print("Background audio session error: \(error)")
        }
    }

    private func setupHighResCamera() {
        captureSession.beginConfiguration()

        // Configure highest resolution (4K 2160p or 1080p fallback)
        if captureSession.canSetSessionPreset(.hd4K3840x2160) {
            captureSession.sessionPreset = .hd4K3840x2160
        } else if captureSession.canSetSessionPreset(.hd1920x1080) {
            captureSession.sessionPreset = .hd1920x1080
        } else {
            captureSession.sessionPreset = .high
        }

        guard let videoDevice = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
              let videoInput = try? AVCaptureDeviceInput(device: videoDevice) else { return }

        if captureSession.canAddInput(videoInput) {
            captureSession.addInput(videoInput)
        }

        let videoOutput = AVCaptureVideoDataOutput()
        videoOutput.alwaysDiscardsLateVideoFrames = true
        videoOutput.setSampleBufferDelegate(self, queue: DispatchQueue(label: "camera.frame.queue"))
        
        if captureSession.canAddOutput(videoOutput) {
            captureSession.addOutput(videoOutput)
        }

        captureSession.commitConfiguration()
        captureSession.startRunning()
    }

    private func startUSBListener() {
        do {
            let parameters = NWParameters.tcp
            listener = try NWListener(using: parameters, on: 9999)
            listener?.stateUpdateHandler = { state in
                print("USB TCP Server Listener State: \(state)")
            }
            listener?.newConnectionHandler = { [weak self] connection in
                self?.activeConnection = connection
                connection.start(queue: .global())
            }
            listener?.start(queue: .global())
        } catch {
            print("Failed to start TCP listener on port 9999: \(error)")
        }
    }

    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard let connection = activeConnection, connection.state == .ready else { return }
        guard let imageBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        
        let ciImage = CIImage(cvImageBuffer: imageBuffer)
        let context = CIContext()
        guard let cgImage = context.createCGImage(ciImage, from: ciImage.extent) else { return }
        let uiImage = UIImage(cgImage: cgImage)
        
        if let jpegData = uiImage.jpegData(compressionQuality: 0.85) {
            var size = UInt32(jpegData.count).bigEndian
            let header = Data(bytes: &size, count: 4)
            connection.send(content: header + jpegData, completion: .contentProcessed({ _ in }))
        }
    }
}
