# A cooked axis-aligned box hull (RnHull_t), as the bake writes it

Read from data, not a DLL: de_dust2's `maps/de_dust2/entities/unnamed_2_23465.vmdl` (its CT `func_buyzone`, a box
x -1196..-312, y -1016..-632, z 0..288) in `web/public/maps/de_dust2/physics.bin` (rubikon/src/Physics/PhysFile.cs's
layout: Valve's own cooked shape copied through VRF by bake/RubikonBake.cs). Other box models of de_dust2's entities
(unnamed_2_23316, 23326, 23467, 23513_7490, ...) have the same tables. Used by `web/src/world/box-physics.js` to make
box models the game adds (a 1v1's section walls, docs/MAP_SECTIONS.md), laid out as these.

## The model (VPhysXAggregateData_t reduced)

- surfaces: one hash, 1977497166 ("default")
- collision attributes: one entry, interacts-as / with / exclude all empty, group "default" (a brush entity's model: the
  entity's class record supplies the layers, rubikon BrushPhysics.Record)
- one part: flags 0, mass 0, inertia scale 1, linear / angular damping 0, linear / angular drag 1, no mass centre
  override, identity transform (1 0 0 0 / 0 1 0 0 / 0 0 1 0)
- one shape: type 2 (hull), attribute index 0, surface index 0

## The hull

Vertex positions, 8, by sign: vertex i has x max unless bit 0 is set, y max unless bit 1, z max unless bit 2:
(x1 y1 z1), (x0 y1 z1), (x1 y0 z1), (x0 y0 z1), (x1 y1 z0), (x0 y1 z0), (x1 y0 z0), (x0 y0 z0).

Planes, 6, as n . p = d, in this order: (0, 1, 0) y1; (0, 0, -1) -z0; (0, -1, 0) -y0; (1, 0, 0) x1; (0, 0, 1) z1;
(-1, 0, 0) -x0.

Topology (bytes): per vertex one outgoing half-edge `20 18 16 22 14 4 6 10`; half-edges (next, twin, origin, face), 24:

```
(21 1 5 0) (11 0 1 5) (5 3 0 0) (17 2 4 3) (14 5 5 1) (0 4 4 0) (10 7 6 1) (13 6 7 2)
(22 9 2 2) (16 8 3 4) (4 11 7 1) (23 10 5 5) (15 13 2 3) (8 12 6 2) (6 15 4 1) (3 14 6 3)
(20 17 2 4) (12 16 0 3) (9 19 1 4) (1 18 3 5) (18 21 0 4) (2 20 1 0) (7 23 3 2) (19 22 7 5)
```

per face one half-edge `0 4 8 12 16 11`; no region SVM.

The derived fields, each checked against this hull's stored value (sides dx 884, dy 384, dz 288):

| Field | Value | Rule |
|---|---|---|
| centroid | (-754, -824, 144) | the box's middle |
| bounds | the box | |
| orthographic areas | (1, 1, 1) | as stored (not the areas) |
| volume | 97,763,328 | dx dy dz |
| surface area | 1,409,280 | 2 (dx dy + dx dz + dy dz) |
| max angular radius | 502.955 | the half diagonal |
| min centroid radius | 144 | the smallest half side (RnHullBuilder.CentroidRadius over the planes) |
| mass properties (row-major 3 x 4) | 1.877e12 0 0 -754 / 0 7.042e12 0 -824 / 0 0 7.568e12 144 | the inertia diagonal V (b^2 + c^2) / 12 per axis, the centroid in the fourth column |
| flags | 3 | |

Unread: what flags 3 means bit by bit, and whether a box hull Valve cooks at another size or orientation ever lists its
tables in another order (every axis-aligned box model of de_dust2's entities checked has these).
