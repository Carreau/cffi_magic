# CFFI magi

Quick iteration of cffi in notebooks.


```python
%%cffi int quint(int);
int quint(int n)
{
    return 5*n;
}

# quint(9) # 45
```

# rust magic

If you have rust installed:

```
%%rust int double(int);

#[no_mangle]
pub extern fn double(x: i32) -> i32 {
    x*2
}

# double(6) # 12
```

