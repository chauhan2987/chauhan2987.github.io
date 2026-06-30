source "https://rubygems.org"

# This is the magic line: the `github-pages` gem bundles the EXACT Jekyll
# version (and exact plugin versions) that GitHub's servers use to build
# Pages sites. Building locally with this Gemfile means "if it builds here,
# it will build identically on GitHub" — no version-mismatch surprises.
gem "github-pages", group: :jekyll_plugins

# Only plugins on GitHub's safe-mode allowlist will actually run when
# GitHub builds your site (https://pages.github.com/versions/). The ones
# below are all on that list and are useful for an academic site.
group :jekyll_plugins do
  gem "jekyll-seo-tag"
  gem "jekyll-sitemap"
end

# Windows/JRuby compatibility shims some `github-pages` dependencies need.
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end
gem "wdm", "~> 0.1.1", platforms: [:mingw, :x64_mingw, :mswin]
