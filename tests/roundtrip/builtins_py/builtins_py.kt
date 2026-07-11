package roundtrip.builtins_py

fun <T> MutableList<T>.append(item: T) {
    this.add(item)
}

fun <K, V> MutableMap<K, V>.get(key: K): V? {
    return this[key]
}

fun str(obj: Any?): String {
    return obj.toString()
}

fun bool_str(obj: Boolean): String {
    return if (obj) "True" else "False"
}

fun String.format(vararg args: Any?): String {
    var result = this
    for (arg in args) {
        result = result.replaceFirst("{}", arg.toString())
    }
    return result
}

fun <T> len(iterable: Collection<T>): Int {
    return iterable.size
}

fun len(str: String): Int {
    return str.length
}

fun <K, V> len(map: Map<K, V>): Int {
    return map.size
}

fun range(start: Int, stop: Int): IntProgression {
    return start until stop
}
