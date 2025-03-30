[app]
title = Payment App
package.name = paymentapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3,kivy==2.2.1,stripe==7.11.0,python-dotenv==1.0.0

orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.1

fullscreen = 0
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1 