# Layout Object Flags (the `<Options>` bit field)

Every `LayoutObject` in a Save a Copy as XML export carries an `<Options>` element right after `<Bounds>`. It is a bit field, and it is the only place the export records how an object is anchored to the layout edges. `layout_to_summary.py` decodes it into `anchor`, `slide`, and `flags`.

## Anchoring: a set bit means anchored

| Bit | Edge |
|-----|------|
| `0x10000000` | left |
| `0x20000000` | top |
| `0x40000000` | right |
| `0x80000000` | bottom |

`0x30000000` is left + top, which is FileMaker's default anchoring. About 98% of the objects in a 15,716-object solution carry it.

**Do not read the left and top bits as "don't anchor".** That reading makes the default object anchored to no edge, and it is wrong. In the same solution, a wide text object that the Inspector shows anchored left, top, and right exports as `0x70000000`. The "don't anchor" reading would say right only.

Common values:

| Value | Anchored | Typical objects |
|-------|----------|-----------------|
| `0x30000000` | left, top | almost everything |
| `0x70000000` | left, top, right | wide text, toolbars |
| `0xB0000000` | left, top, bottom | portals, tab controls, panels that grow with the window |
| `0xF0000000` | all four | tab controls and panels that fill the window |

## Other bits

Four of these bits have an XML counterpart, so the export lets you check them. In the same 15,716 objects:

| Bit | Meaning | Check |
|-----|---------|-------|
| `0x0001` | has conditional formatting | set on 330 objects, and those are exactly the objects with a `<Formatting>` condition |
| `0x0004` | has a hide condition | set on 1,557 objects, and those are exactly the objects with a `<Hide>` |
| `0x0100` | evaluate the hide condition in Find mode | set on all 227 objects whose `<Hide>` has `findMode="True"`, and also on 35 that have no such hide, so it is not exact |
| `0x4000` | has a tooltip | set on 757 objects, and those are exactly the objects with a `<Tooltip>` |

These bits have no XML counterpart to check against, so they are decoded from the Claris grammar and not confirmed here: `0x0002` locked, `0x0010` slide up, `0x0020` slide left, `0x0200` don't image when printing, `0x10000` hand cursor over button.

## How much of this was checked in FileMaker

Only one anchor value was compared against the Inspector: `0x70000000` shows left, top, and right. The right and bottom bits are also consistent with where they appear (bottom on portals and tab controls, which stretch with the window), but treat each as unconfirmed until you compare an object of that value against its Inspector Anchor boxes.

## Traps

- **Same element name, different meaning.** A `<Portal>` has its own inner `<Options show="…">`, and a `<Field>` uses `<Options>` for its number format. Only the `<Options>` that is a direct child of the `LayoutObject` holds these flags.
- **Regex over nested objects miscounts.** A Hide, Tooltip, or Options inside a portal or group belongs to the nested object, not the group. Walk the XML tree instead of matching text, or every ancestor claims its children's settings.
- **Count what you matched.** A non-greedy pattern with a length cap silently skips large objects. A clean result over 3 portals looked like proof until the count showed 81 of 84 had been dropped.

## References

| Name | Type | Where |
|------|------|-------|
| `layout_to_summary.py` | script | `agent/scripts/layout_to_summary.py` (`parse_object_flags`) |
| Theme and LocalCSS cascade | knowledge article | `agent/docs/knowledge/theme-layout-css.md` |
| Database Design Report XML grammar | Claris reference | [Claris FileMaker Pro 19 archive](https://help.claris.com/archive/fm19/en/pro-db-design-report-xml-grammar/) |
