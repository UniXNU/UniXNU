# Documentation site

The documentation is a VitePress site in `docs/`. It is published to `https://unixnu.com`.

## Procedure {#procedure}

1. Identify the owning page and its English/Chinese counterpart. For device results, update the device's [structured record](#device-records).
2. Edit the current procedure or reference. An operation needs prerequisites, working directory, ordered commands, expected results and the next step.
3. Link the page from the relevant workflow. Follow [Add a page](#add-a-page) for navigation and locale entries.
4. Run `npm --prefix docs run build` from the main checkout. Resolve build errors, then follow body links from [Port a device](/porting/steps) and [Technical reference](/reference/) to the changed page in both languages.
5. Preview the page using [local development](#local-development), check its command blocks and next-step links, then publish the documentation commit.

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

Format 2 device pages follow [record publication](/porting/records#publishing-and-reuse). Use these steps for authored guides.

1. Create the Markdown file under the matching section.
2. Add the page to the sidebar in `docs/.vitepress/config.mts`.
3. Add the Chinese page under `docs/zh/` and to the Chinese sidebar.
4. Link the page from a relevant guide or topic index reachable from [Port a device](/porting/steps). Put task prerequisites and the next step in the page body.
5. Follow the body links from Port a device in each language to confirm the page is reachable.
6. Run `npm run build` and fix broken links.
7. Add the language switcher entry when a new section starts.

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
- Number task steps in execution order and include inputs, working directory, commands, expected results and the next step. Reference pages link to the relevant procedure.

## Link check

```sh
cd docs
npm run build
```

VitePress fails the build on a broken internal link.

## Next steps

- [Repository layout](/contributing/repository)
- [Port a device](/porting/steps)

## Device records

Site builds require Python 3.11 or newer. `npm run build` renders the committed
catalog and record snapshots. The twice-daily catalog workflow discovers sources,
pins revisions and refreshes format 2 pages, the index and navigation.
Edit `porting.toml` in the device repository and publish it. Both language
editions use the same record. Existing legacy pages retain their authored text;
new legacy entries contain a repository link. See the [record guide](/porting/records#publishing-and-reuse).

## Driver guides

Organize steps by hardware inputs, interface implementation, OS integration,
build and verification. Link real source files at reviewed revisions and name
the relevant symbols, call order, data ownership and error handling. Use board
sources as references and keep device status in device records. Each step states
what to change and how to observe its result. Use matching source references in
the English and Chinese editions.

A porting page links other porting pages for adaptation steps. Component pages
under `drivers/` are reference and are reached from [Technical reference](/reference/).
