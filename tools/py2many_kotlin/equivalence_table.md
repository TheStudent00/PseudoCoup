# Construct-equivalence table (harvested from py2many source)

Declarative rows only. Structural constructs (if/for/while/class/operators) are imperative emit-templates, not rows -- see run_atlas.sh.

Backends read: 7 (Kotlin, Rust, Go, Nim, Julia, Zig, Mojo)

## Primitive types

| Python | Kotlin | Rust | Go | Nim | Julia | Zig | Mojo |
|---|---|---|---|---|---|---|---|
| `bool` | Boolean | bool | bool | bool | Bool | bool | Bool |
| `int` | Int | i32 | int | int | Int64 | i32 | Int |
| `float` | Double | f64 | float64 | float64 | Float64 | f64 | Float64 |
| `bytes` | ByteArray | &[u8] | []uint8 | openArray[byte] | Vector{UInt8} | []u8 | SIMD[DType.uint8] |
| `str` | String | &str | string | string | String | []const u8 | String |
| `c_byte` | Byte | i8 | int8 | int8 | Int8 | i8 | Int8 |
| `c_short` | Short | i16 | int16 | int16 | Int16 | i16 | Int16 |
| `c_int` | Int | i32 | int32 | int32 | Int32 | i32 | Int32 |
| `c_long` | Long | i64 | int64 | int64 | Int64 | i64 | Int64 |
| `c_ubyte` | UByte | u8 | uint8 | uint8 | UInt8 | u8 | UInt8 |
| `c_ushort` | UShort | u16 | uint16 | uint16 | UInt16 | u16 | UInt16 |
| `c_uint` | UInt | u32 | uint32 | uint32 | UInt32 | u32 | UInt32 |
| `c_ulong` | ULong | u64 | uint64 | uint64 | UInt64 | u64 | UInt64 |
| `RawIOBase` | · | std::fs::File | · | · | · | · | · |
| `bytearray` | · | · | · | · | · | []u8 | SIMD[DType.uint8] |


## Container types

| Python | Kotlin | Rust | Go | Nim | Julia | Zig | Mojo |
|---|---|---|---|---|---|---|---|
| `List` | Array | Vec | [] | seq | Vector | pylib.AutoArrayList | List |
| `Dict` | HashMap | HashMap | · | Table | Dict | pylib.AutoMap | Dict |
| `Set` | Set | HashSet | · | set | Set | pylib.AutoSet | Set |
| `Optional` | Nothing | Option | nil | Option | Union{Nothing} | Optional | Optional |
| `Result` | · | Result | · | · | · | · | · |


## Stdlib / builtin functions with a mapping (coverage; emitted form verified via the compile gate)

- **Kotlin** (14): `abs`, `bool`, `float`, `floor`, `int`, `len`, `math.sqrt`, `max`, `min`, `print`, `range`, `reversed`, `str`, `xrange`
- **Rust** (26): `asyncio.run`, `bool`, `enumerate`, `filter`, `float`, `floor`, `i16`, `i32`, `i64`, `i8`, `int`, `len`, `list`, `map`, `max`, `min`, `print`, `range`, `reversed`, `str`, `sum`, `u16`, `u32`, `u64`, `u8`, `xrange`
- **Go** (11): `bool`, `float`, `floor`, `int`, `max`, `min`, `print`, `range`, `range_`, `str`, `xrange`
- **Nim** (8): `bool`, `float`, `floor`, `int`, `print`, `range`, `str`, `xrange`
- **Julia** (10): `bool`, `enumerate`, `floor`, `int`, `len`, `print`, `range`, `str`, `sum`, `xrange`
- **Zig** (7): `bool`, `float`, `floor`, `int`, `print`, `range`, `str`
- **Mojo** (6): `bool`, `float`, `floor`, `int`, `print`, `str`


## Compile-verified overrides (source intent was wrong)

| Language | Pivot | Verified value |
|---|---|---|
| Kotlin | `Optional` | `T?`  (source says `Nothing` — wrong; fixed in pykt.patch, kotlinc-verified) |
