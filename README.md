#muu

a decorator providing multiline lambdas for Python3

```python
@muu
def wat(x):
	return map(lam(e)[
		print(e),
		len(e)], x)

wat(['a', 'hello']) # print e and hello, 
# [1, 5]
```

it supports assignment with `<-`

```python
from muu import muu

@muu
def ok(x):
	return map(lam(e)[
		x['name'] <~ "ha",
		x], x)

ok([{'name': 2}]) # [{'name': 'ha'}]
```

##implementation

a decorator which patches bytecode of decorated function: replaces lam macro invocations with
bytecode for an equivalent lambda (the limitation for one expression is only on language/ast level, not in the VM)

dark magic, a horrible hack, but really a lot of fun

## thanks

uses a forked and patched version of byteplay. Credits to [https://wiki.python.org/moin/ByteplayDoc](https://wiki.python.org/moin/ByteplayDoc) and [https://github.com/serprex/byteplay](https://github.com/serprex/byteplay)
