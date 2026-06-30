i feel like we should break away from lambdas unless there is a very specific reason why we need them. i mean in terms of what a lambda gets mapped into. i would rather a default to the numbered lambda as youve described.


```
def _lam29(it=None):
    append(f'"{...}" is in {where}. ')      # <-- BARE append
    if prompt.substituteName != None:
        return append("Swap it for ...")     # <-- BARE append
    ...
return Text(buildString(_lam29))             # <-- buildString also bare
```

could you show me the above but where you include the original Kotlin for it. i want to see how things are being mapped to the above because the example you gave makes sense to me but the _lam29 contents dont make sense to me.