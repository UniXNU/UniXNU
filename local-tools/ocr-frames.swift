// Recognise the text of video frames with macOS Vision.
//   swift ocr-frames.swift FRAME.png [FRAME.png ...]            each recognised line once, in frame order
//   swift ocr-frames.swift --boxes FRAME.png [FRAME.png ...]    every piece of text with its place in the frame
//   swift ocr-frames.swift --fast FRAME.png [FRAME.png ...]     use Vision's fast recognition mode
// Used to read the sheng firmware and kernel console from a phone recording of the tablet screen.
//
// Vision returns a console line with wide gaps between its columns as several pieces. --boxes prints one piece a line
// as "<frame>\t<top>\t<left>\t<height>\t<text>" (top, left and height as fractions of the frame, top measured from the
// top edge), so the pieces of each console line can be grouped by their coordinates.
import Foundation
import Vision
import AppKit

var arguments = Array(CommandLine.arguments.dropFirst())
let boxes = arguments.contains("--boxes")
let fast = arguments.contains("--fast")
arguments.removeAll { $0 == "--boxes" || $0 == "--fast" }

var seen = Set<String>()
var failed = false
for path in arguments {
    guard let image = NSImage(contentsOfFile: URL(fileURLWithPath: path).path),
          let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        fputs("\(path): cannot read image\n", stderr)
        failed = true
        continue
    }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = fast ? .fast : .accurate
    request.usesLanguageCorrection = false
    do {
        try VNImageRequestHandler(cgImage: cg, options: [:]).perform([request])
    } catch {
        fputs("\(path): \(error)\n", stderr)
        failed = true
        continue
    }
    let name = (path as NSString).lastPathComponent
    let results = (request.results ?? []).sorted { $0.boundingBox.minY > $1.boundingBox.minY }
    for result in results {
        guard let line = result.topCandidates(1).first?.string else { continue }
        if boxes {
            let box = result.boundingBox
            print(String(format: "%@\t%.5f\t%.5f\t%.5f\t%@", name, 1 - box.maxY, box.minX, box.height, line))
        } else if !seen.contains(line) {
            seen.insert(line)
            print("\(name): \(line)")
        }
    }
}

if failed { exit(EXIT_FAILURE) }
