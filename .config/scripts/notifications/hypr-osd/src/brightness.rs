use crate::notification;
use std::process::Command;

pub fn run(args: &[String]) {
    let action = args.get(0).map(|arg| arg.as_str()).unwrap_or("");
    let step = args.get(1).map(|arg| arg.as_str()).unwrap_or("5");

    match action {
        "up" => {
            Command::new("brightnessctl")
                .args(["set", &format!("{step}%+")])
                .status()
                .ok();
        }
        "down" => {
            Command::new("brightnessctl")
                .args(["set", &format!("{step}%-")])
                .status()
                .ok();
        }
        _ => return,
    }

    let current = Command::new("brightnessctl")
        .args(["get"])
        .output()
        .unwrap();
    let current = String::from_utf8_lossy(&current.stdout);

    let max = Command::new("brightnessctl")
        .args(["max"])
        .output()
        .unwrap();
    let max = String::from_utf8_lossy(&max.stdout);

    let current: u32 = current.trim().parse().unwrap_or(0);
    let max: u32 = max.trim().parse().unwrap_or(1);
    let percentage = current * 100 / max;

    notification::send("brightness", 9991, 1000, &format!("Brightness {percentage}%"), "");
}
