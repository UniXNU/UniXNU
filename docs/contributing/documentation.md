# Documentation site

The documentation is a VitePress site in `docs/`. It is published to `https://unixnu.com`.

## Requirements

| Tool | Version |
| --- | --- |
| Node.js | 22 or newer |
| npm | 10 or newer |

## Local development

```sh
cd docs
npm install
npm run dev
```

The site runs at the URL printed by VitePress. `npm run build` writes the static site to `docs/.vitepress/dist`. `npm run preview` serves the built site.

## Structure

```
docs/
  .vitepress/
    config.mts          site configuration
    theme/              custom CSS
  public/
    CNAME               custom domain
    logo-light.svg
    logo-dark.svg
  guide/                getting started and build
  concepts/             boot chain, payload, prelink, userdata, security
  porting/              device porting
  drivers/              UEFI, XNU and kext drivers
  xnu/                  source, patches, pages, boot arguments
  devices/              device pages and examples
  reference/            command line, configuration, outputs, QEMU, glossary
  contributing/         this section
  zh/                   Simplified Chinese locale
```

## Add a page

1. Create the Markdown file under the matching section.
2. Add the page to the sidebar in `docs/.vitepress/config.mts`.
3. Add the Chinese page under `docs/zh/` and to the Chinese sidebar.
4. Run `npm run build` and fix broken links.
5. Add the language switcher entry when a new section starts.

## Language editions

The site has two locales:

| Locale | Path | Language |
| --- | --- | --- |
| Root | `/` | English |
| `zh` | `/zh/` | Simplified Chinese |

Both editions carry the same pages. A change to one page updates both editions in the same pull request.

## Writing rules

- Use standard technical terms.
- State the current behavior directly.
- Avoid em-dashes and en-dashes.
- Avoid metaphors.
- Use neutral headings.
- Keep the page focused on one subject.
- Use tables for references and lists for steps.
- Put device-specific values in the device page.
- Put a concrete command in every procedure.

## Link check

```sh
cd docs
npm run build
```

VitePress fails the build on a broken internal link.

## Next steps

- [Repository layout](/contributing/repository)
- [Overview](/guide/overview)
