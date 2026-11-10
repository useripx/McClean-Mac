cask "mrclean" do
  version "2.0.0"
  sha256 :no_check

  url "https://github.com/useripx/McClean-Mac/releases/download/v#{version}/MrClean-macOS.dmg"
  name "MrClean Mac"
  desc "Offline Metadata Inspector, Cleaner, Presets & AI Watermarks Remover"
  homepage "https://github.com/useripx/McClean-Mac"

  livecheck do
    url :url
    strategy :github_latest
  end

  auto_updates true
  depends_on macos: ">= :catalina"

  app "MrClean.app"
  binary "#{appdir}/MrClean.app/Contents/MacOS/MrClean", target: "mrclean"

  zap trash: [
    "~/Library/Application Support/MrClean",
    "~/Library/Preferences/com.useripx.mrclean.plist",
    "~/Library/Saved Application State/com.useripx.mrclean.savedState",
  ]
end
