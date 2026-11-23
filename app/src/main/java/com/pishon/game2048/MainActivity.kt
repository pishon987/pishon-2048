package com.pishon.game2048

import android.annotation.SuppressLint
import android.app.Activity
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.os.Build
import android.os.Bundle
import android.view.View
import android.view.ViewGroup.LayoutParams.MATCH_PARENT
import android.view.WindowInsets
import android.view.WindowInsetsController
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout

/**
 * Single-screen 2048 game. The whole game runs from one bundled HTML page in
 * assets, so the app needs no network access and no runtime permissions.
 */
class MainActivity : Activity() {

    private lateinit var webView: WebView
    private lateinit var root: FrameLayout

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val background = Color.parseColor("#FAF8EF")
        window.setBackgroundDrawable(ColorDrawable(background))

        // From Android 15 (API 35) the system draws every app edge to edge,
        // whatever the app asks for. Older versions are switched to the same
        // mode so that one code path handles the window insets everywhere.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            window.setDecorFitsSystemWindows(false)
        }

        // The insets are applied as padding on this container rather than on the
        // WebView itself: a WebView paints its page over its whole bounds and
        // ignores its own padding, which let the header slide under the status
        // bar and the hint text under the navigation bar on Android 15.
        root = FrameLayout(this).apply {
            setBackgroundColor(background)
            clipToPadding = true
            fitsSystemWindows = false
        }

        webView = WebView(this).apply {
            setBackgroundColor(background)
            overScrollMode = View.OVER_SCROLL_NEVER
            isVerticalScrollBarEnabled = false
            isHorizontalScrollBarEnabled = false
            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                allowContentAccess = false
                setSupportZoom(false)
                builtInZoomControls = false
                displayZoomControls = false
                mediaPlaybackRequiresUserGesture = true
                textZoom = 100
                cacheMode = WebSettings.LOAD_NO_CACHE
            }
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(
                    view: WebView?,
                    request: android.webkit.WebResourceRequest?
                ): Boolean {
                    val url = request?.url?.toString() ?: return true
                    return !url.startsWith("file:///android_asset/")
                }
            }
        }

        root.addView(
            webView,
            FrameLayout.LayoutParams(MATCH_PARENT, MATCH_PARENT)
        )
        setContentView(
            root,
            android.view.ViewGroup.LayoutParams(MATCH_PARENT, MATCH_PARENT)
        )

        applySafeAreaInsets()
        applySystemBarStyle()

        if (savedInstanceState == null || webView.restoreState(savedInstanceState) == null) {
            webView.loadUrl("file:///android_asset/index.html")
        }
    }

    /** Keeps the page clear of the status bar, navigation bar and camera cutout. */
    private fun applySafeAreaInsets() {
        root.setOnApplyWindowInsetsListener { view, insets ->
            val left: Int
            val top: Int
            val right: Int
            val bottom: Int
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                val bars = insets.getInsets(
                    WindowInsets.Type.systemBars() or WindowInsets.Type.displayCutout()
                )
                left = bars.left
                top = bars.top
                right = bars.right
                bottom = bars.bottom
            } else {
                @Suppress("DEPRECATION")
                run {
                    left = insets.systemWindowInsetLeft
                    top = insets.systemWindowInsetTop
                    right = insets.systemWindowInsetRight
                    bottom = insets.systemWindowInsetBottom
                }
            }
            if (view.paddingLeft != left || view.paddingTop != top ||
                view.paddingRight != right || view.paddingBottom != bottom
            ) {
                view.setPadding(left, top, right, bottom)
            }
            insets
        }
        root.requestApplyInsets()
    }

    private fun applySystemBarStyle() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            val lightMask =
                WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS or
                    WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS
            window.insetsController?.setSystemBarsAppearance(lightMask, lightMask)
        } else {
            @Suppress("DEPRECATION")
            run {
                window.statusBarColor = Color.parseColor("#FAF8EF")
                window.navigationBarColor = Color.parseColor("#FAF8EF")
                var flags = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    flags = flags or View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR
                }
                window.decorView.systemUiVisibility = flags
            }
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        webView.saveState(outState)
    }

    override fun onPause() {
        super.onPause()
        webView.onPause()
    }

    override fun onResume() {
        super.onResume()
        webView.onResume()
    }

    override fun onDestroy() {
        webView.destroy()
        super.onDestroy()
    }
}
