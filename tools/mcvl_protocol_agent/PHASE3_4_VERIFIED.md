# Phase 3.4 — Runtime Source Extraction / Verification

## Status: VERIFIED (for supplied archive)

Verified archive:
- `MCVL_Godot_Android_Landscape.zip`
- size: 5,699,723 bytes
- SHA-256: `e59cbfa6a12f723c47bbc0e53d6805fd8c410cf200d98bf482e7a2402886eda1`
- ZIP entries: 2,424

## Source inventory

The archive contains 4 GDScript files:

- `Game.gd`
- `MapCamera.gd`
- `WorldMap.gd`
- `MapPlayer.gd`

It also contains `project.godot` and `Game.tscn`.

## Runtime finding

This archive is a **Godot Android landscape map/runtime reconstruction**. The source implements:

```
Game.gd
  -> MCVWorldMap.load_map()
  -> MCVMapPlayer
  -> MCVMapCamera
  -> map drawing / collision
```

The supplied source contains **no verified TCP/socket/network receive layer**, no packet decoder, and no packet dispatcher.

A source scan found no TCP/UDP/socket symbols in the 4 GDScript files.

Therefore:

- Phase 3.4 source extraction: **VERIFIED**
- Network integration point: **NOT PRESENT IN THIS ARCHIVE**
- PacketCapture runtime wiring: **BLOCKED**
- No runtime source was modified.

## Consequence

The previous planned boundary:

```
socket receive -> frame reconstruction -> PacketCapture -> dispatcher
```

cannot be instantiated against this archive because the first two stages do not exist here.

The correct next source target is the MCVL APK/server/network implementation that produced the observed log:

```
127.0.0.1:9001
RX_FRAME
RX_FRAME_HEX
RX_PACKET pid=1026
FRAME_HANDLED
TX_RESPONSE
```

That implementation is separate from this map-only Godot project.

## Phase 3.5 gate

Do not wire `PacketCaptureAdapter` into `Game.gd`, `WorldMap.gd`, `MapPlayer.gd`, or `MapCamera.gd`. None is a network integration point.

Phase 3.5 requires the actual server/network source or decompiled source containing the TCP receive/frame/dispatch path.
