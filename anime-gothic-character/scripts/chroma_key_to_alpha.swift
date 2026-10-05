#!/usr/bin/env swift

import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

guard CommandLine.arguments.count == 4 else {
    fputs("usage: chroma_key_to_alpha.swift green|blue input.png output.png\n", stderr)
    exit(2)
}

let keyChannel: Int
switch CommandLine.arguments[1] {
case "green": keyChannel = 1
case "blue": keyChannel = 2
default:
    fputs("key color must be green or blue\n", stderr)
    exit(2)
}

let inputURL = URL(fileURLWithPath: CommandLine.arguments[2]) as CFURL
let outputURL = URL(fileURLWithPath: CommandLine.arguments[3]) as CFURL
guard
    let source = CGImageSourceCreateWithURL(inputURL, nil),
    let image = CGImageSourceCreateImageAtIndex(source, 0, nil),
    let colorSpace = CGColorSpace(name: CGColorSpace.sRGB)
else {
    fputs("could not read input image\n", stderr)
    exit(3)
}

let width = image.width
let height = image.height
let bytesPerPixel = 4
let bytesPerRow = width * bytesPerPixel
var pixels = [UInt8](repeating: 0, count: height * bytesPerRow)

guard let context = CGContext(
    data: &pixels,
    width: width,
    height: height,
    bitsPerComponent: 8,
    bytesPerRow: bytesPerRow,
    space: colorSpace,
    bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue |
        CGBitmapInfo.byteOrder32Big.rawValue
) else { exit(4) }

context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))

func nonKeyMaximum(at offset: Int) -> Int {
    if keyChannel == 1 {
        return max(Int(pixels[offset]), Int(pixels[offset + 2]))
    }
    return max(Int(pixels[offset]), Int(pixels[offset + 1]))
}

func applyKey(at offset: Int, dominanceThreshold: Int, alphaCeiling: Int = 255) {
    let key = Int(pixels[offset + keyChannel])
    let nonKey = nonKeyMaximum(at: offset)
    guard key > 80 && key - nonKey > dominanceThreshold else { return }

    var alpha = max(0, min(alphaCeiling, 255 - key + nonKey))
    if alpha < 48 { alpha = 0 }
    for channel in 0..<3 {
        let value = channel == keyChannel ? nonKey : Int(pixels[offset + channel])
        pixels[offset + channel] = UInt8(min(value, alpha))
    }
    pixels[offset + 3] = UInt8(alpha)
}

var transparentMask = [Bool](repeating: false, count: width * height)
for index in 0..<(width * height) {
    let offset = index * bytesPerPixel
    applyKey(at: offset, dominanceThreshold: 24)
    transparentMask[index] = pixels[offset + 3] == 0
}

var distance = [Int8](repeating: -1, count: width * height)
var queue = [Int]()
for index in 0..<transparentMask.count where transparentMask[index] {
    distance[index] = 0
    queue.append(index)
}

var cursor = 0
while cursor < queue.count {
    let index = queue[cursor]
    cursor += 1
    let currentDistance = distance[index]
    if currentDistance >= 4 { continue }

    let x = index % width
    let y = index / width
    for dy in -1...1 {
        for dx in -1...1 where dx != 0 || dy != 0 {
            let nextX = x + dx
            let nextY = y + dy
            guard nextX >= 0, nextX < width, nextY >= 0, nextY < height else { continue }
            let next = nextY * width + nextX
            if distance[next] == -1 {
                distance[next] = currentDistance + 1
                queue.append(next)
            }
        }
    }
}

for index in 0..<distance.count where distance[index] > 0 && distance[index] <= 4 {
    let offset = index * bytesPerPixel
    applyKey(
        at: offset,
        dominanceThreshold: 2,
        alphaCeiling: Int(pixels[offset + 3])
    )
}

var transparentCount = 0
var partialCount = 0
for offset in stride(from: 3, to: pixels.count, by: bytesPerPixel) {
    if pixels[offset] == 0 { transparentCount += 1 }
    else if pixels[offset] < 255 { partialCount += 1 }
}

guard transparentCount >= width * height / 20 else {
    fputs("fewer than 5% of pixels became transparent; check the selected key color\n", stderr)
    exit(5)
}

guard
    let outputContext = CGContext(
        data: &pixels,
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: bytesPerRow,
        space: colorSpace,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue |
            CGBitmapInfo.byteOrder32Big.rawValue
    ),
    let outputImage = outputContext.makeImage(),
    let destination = CGImageDestinationCreateWithURL(
        outputURL,
        UTType.png.identifier as CFString,
        1,
        nil
    )
else { exit(6) }

CGImageDestinationAddImage(destination, outputImage, nil)
guard CGImageDestinationFinalize(destination) else { exit(7) }

print("converted \(width)x\(height): \(transparentCount) transparent, \(partialCount) partial pixels")
