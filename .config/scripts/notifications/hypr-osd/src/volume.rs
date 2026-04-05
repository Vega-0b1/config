use crate::notification;
use std::process::Command;

pub fn run(args: &[String]) {
    let action = args.get(0).map(|arg| arg.as_str()).unwrap_or("");
    let step = args.get(1).map(|arg| arg.as_str()).unwrap_or("5");
    let sink = "@DEFAULT_AUDIO_SINK@";

    match action {
        "up" => {
            Command::new("wpctl")
                .args(["set-mute", sink, "0"])
                .status()
                .ok();
            Command::new("wpctl")
                .args(["set-volume", sink, &format!("{step}%+"), "--limit", "1.0"])
                .status()
                .ok();
        }
        "down" => {
            Command::new("wpctl")
                .args(["set-mute", sink, "0"])
                .status()
                .ok();
            Command::new("wpctl")
                .args(["set-volume", sink, &format!("{step}%-")])
                .status()
                .ok();
        }
        "mute" => {
            Command::new("wpctl")
                .args(["set-mute", sink, "toggle"])
                .status()
                .ok();
        }
        _ => return,
    }

    let out = Command::new("wpctl")
        .args(["get-volume", sink])
        .output()
        .unwrap();
    let out = String::from_utf8_lossy(&out.stdout);

    let muted = out.contains("[MUTED]");

    let vol: f32 = out
        .split_whitespace()
        .nth(1)
        .and_then(|arg| arg.parse().ok())
        .unwrap_or(0.0);

    let percentage = (vol * 100.0).round() as u32;

    if muted {
        notification::send("volume", 9990, 1000, "Volume Muted", "");
    } else {
        notification::send("volume", 9990, 1000, &format!("Volume {percentage}%"), "");
    }
}
