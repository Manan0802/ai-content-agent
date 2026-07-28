"""Build the review gallery from library/ into web/public/.

    python -m scripts.build_gallery

Then deploy (needs a Cloudflare account and `npx wrangler login` once):

    cd web && npx wrangler pages deploy public
"""
from modules.gallery import build_site


def main() -> None:
    manifest = build_site()
    items = manifest["items"]
    total = sum(i["preview_bytes"] for i in items)
    for i in items:
        print(f"  {i['id']:<40} {i['preview_bytes'] / 1048576:>5.1f} MB")
    print(f"\n{len(items)} videos, {total / 1048576:.1f} MB of previews -> web/public/")


if __name__ == "__main__":
    main()
