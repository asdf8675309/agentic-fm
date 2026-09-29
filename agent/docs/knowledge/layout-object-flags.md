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

**Do not read the left and top bits as "don't anchor".** That reading makes the default object anchored to no edge, and it is wrong. Four objects in the same solution were compared against the Inspector. A wide text object shown anchored left, top, and right exports as `0x70000000`, and the "don't anchor" reading would say right only. An edit box shown anchored left and bottom exports as `0x90000000`, and that reading would say bottom only. A tab control shown anchored on all four edges exports as `0xF0000000`, and that reading would say right and bottom. A portal shown anchored top, left, and bottom exports as `0xB0000000`, and that reading would say bottom only.

Common values:

| Value | Anchored | Typical objects |
|-------|----------|-----------------|
| `0x30000000` | left, top | almost everything |
| `0x70000000` | left, top, right | wide text, toolbars (confirmed in the Inspector) |
| `0xB0000000` | left, top, bottom | portals, tab controls, panels that grow with the window (confirmed in the Inspector) |
| `0xF0000000` | all four | tab controls and panels that fill the window (confirmed in the Inspector) |
| `0x90000000` | left, bottom | an edit box pinned to the bottom-left (confirmed in the Inspector) |

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

Four anchor values were compared against the Inspector, one object each: `0x70000000` (left, top, right), `0x90000000` (left, bottom), `0xB0000000` (left, top, bottom), and `0xF0000000` (all four). All four match the "set means anchored" reading and contradict the "don't anchor" reading. Together they cover 90 of the 255 objects in that solution that are not left and top only. The other common values, `0x10000000` (left only, 138 objects) and `0xD0000000` (left, right, bottom, 23 objects), follow from the same bits but were not compared against an Inspector.

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
