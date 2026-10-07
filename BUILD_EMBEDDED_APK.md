# MCVL — Embedded Local Server APK

This branch contains the GitHub Actions build pipeline for the Java ServerSocket version of MCVL.

## Build input

Upload the generated source archive to the repository root as:

`MCVL_EMBEDDED_LOCAL_SERVER_SOURCE.zip`

The archive must contain:

`mcvl-android-source/build_apk.sh`

## Build

Open **Actions → Build MCVL Embedded Local Server APK → Run workflow**.

The workflow installs JDK 17, Android SDK platform 34, and Android Build Tools 34.0.0. It runs the supplied build script, verifies the APK signature, calculates SHA-256, and publishes the APK as a GitHub Actions artifact.

## Runtime

The embedded server listens on `127.0.0.1:9001`. The game endpoint is rewritten from the original remote endpoint to loopback during the build.
