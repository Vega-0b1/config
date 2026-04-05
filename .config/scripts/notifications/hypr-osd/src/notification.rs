use notify_rust::{Hint, Notification};

pub fn send(app: &str, id: u32, timeout: i32, summary: &str, body: &str) {
    Notification::new()
        .appname(app)
        .id(id)
        .timeout(timeout)
        .summary(summary)
        .body(body)
        .hint(Hint::Custom(
            "x-canonical-private-synchronous".to_string(),
            app.to_string(),
        ))
        .show()
        .unwrap();
}
