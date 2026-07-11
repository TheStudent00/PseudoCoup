class ValueError implements Exception {
  String cause;
  ValueError(this.cause);
}

int len(dynamic obj) {
  return obj.length;
}

String str(dynamic obj) {
  return obj.toString();
}

List<int> range(int start, int end) {
  return [for (var i = start; i < end; i++) i];
}

extension ListPy<T> on List<T> {
  void append(T element) {
    this.add(element);
  }
}

extension MapPy<K, V> on Map<K, V> {
  V get(K key) {
    return this[key] as V;
  }
  bool contains(dynamic key) {
    return this.containsKey(key);
  }
}

extension StringPy on String {
  String format(dynamic arg1, [dynamic arg2]) {
    String res = this.replaceFirst('{}', arg1.toString());
    if (arg2 != null) {
      res = res.replaceFirst('{}', arg2.toString());
    }
    return res;
  }
}
