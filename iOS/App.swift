import SwiftUI

@main
struct USBWebcamApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    // Keep a strong reference to the camera manager so it stays alive
    let cameraManager = CameraManager()
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "camera.fill")
                .font(.system(size: 60))
                .foregroundColor(.green)
            Text("USB 4K Webcam Running")
                .font(.headline)
            Text("Leave this app open in the background.\nPlug in USB cable to PC and launch the Windows .exe host.")
                .multilineTextAlignment(.center)
                .padding()
        }
    }
}
