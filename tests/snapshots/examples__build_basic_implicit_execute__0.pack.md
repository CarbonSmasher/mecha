# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 9,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
execute if score @p tmp matches 1 run say hello
execute as @a at @s run setblock ~ ~ ~ stone
execute if score @p tmp matches 1 run say hello
execute as @a at @s run setblock ~ ~ ~ stone
execute if score @p tmp matches 1 run say hello
execute as @a at @s run setblock ~ ~ ~ stone
execute if score @p tmp matches 1 run say hello
execute as @a at @s run setblock ~ ~ ~ stone
execute store result score PLAYER_COUNT global if entity @a
execute store result score PLAYER_COUNT global if entity @a
```
