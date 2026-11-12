import UIKit
import WebKit

// GXB 3 version 1.1.2 — iOS WKWebView shell for the authenticated production VPS.
// No cached or fabricated gameplay; the authoritative game remains on server.
@main
final class GXB3Application: UIResponder, UIApplicationDelegate {
    var window: UIWindow?

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        let window = UIWindow(frame: UIScreen.main.bounds)
        window.rootViewController = GXB3Controller()
        window.makeKeyAndVisible()
        self.window = window
        return true
    }
}

final class GXB3Controller: UIViewController, WKNavigationDelegate {
    private let origin = URL(string: "https://180-93-111-99.sslip.io/?client=ios&v=1.1.2")!
    private var web: WKWebView!
    private let loading = UILabel()

    override var prefersStatusBarHidden: Bool { true }

    override func loadView() {
        let conf = WKWebViewConfiguration()
        conf.defaultWebpagePreferences.allowsContentJavaScript = true
        conf.websiteDataStore = .default()
        conf.allowsInlineMediaPlayback = true
        conf.mediaTypesRequiringUserActionForPlayback = []
        web = WKWebView(frame: .zero, configuration: conf)
        web.navigationDelegate = self
        web.scrollView.contentInsetAdjustmentBehavior = .never
        web.isOpaque = false
        web.backgroundColor = UIColor(red: 0.07, green: 0.08, blue: 0.13, alpha: 1)
        view = web
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        loading.text = "Nữ Thần Chiến Đấu - GXB 3 · 1.1.2\nĐang kết nối máy chủ…"
        loading.numberOfLines = 0
        loading.textAlignment = .center
        loading.textColor = .white
        loading.font = .systemFont(ofSize: 17, weight: .semibold)
        loading.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(loading)
        NSLayoutConstraint.activate([
            loading.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            loading.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            loading.leadingAnchor.constraint(greaterThanOrEqualTo: view.leadingAnchor, constant: 24)
        ])
        web.load(URLRequest(url: origin, cachePolicy: .reloadIgnoringLocalCacheData))
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        loading.removeFromSuperview()
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        loading.text = "Không thể kết nối máy chủ GXB 3.\nKiểm tra mạng rồi mở lại ứng dụng."
    }

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url else { decisionHandler(.cancel); return }
        if url.scheme == "https", url.host?.lowercased() == origin.host?.lowercased() {
            decisionHandler(.allow)
        } else if let scheme = url.scheme?.lowercased(), ["https", "http", "zalo"].contains(scheme) {
            UIApplication.shared.open(url)
            decisionHandler(.cancel)
        } else {
            decisionHandler(.cancel)
        }
    }
}
