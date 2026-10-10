# lverror

Offline lookup that turns a LabVIEW or NI error code into a human description, with no
LabVIEW and no NI driver installed.

## Install

```
pip install lverror
```

## Usage

```python
import lverror

lverror.explain(7)
# 'File not found. The file might be in a different location or deleted. ...'

lverror.explain(1672)
# 'There was an unknown Python error in the operation.'

lverror.explain(999999)      # not a documented code
# None

info = lverror.describe(-200279)
info.code                    # -200279
info.message                 # None  (no public message for this specific code)
info.family                  # 'NI-DAQmx'  (classified by its range)
info.is_error                # True

lverror.is_error(-1073807339)   # True  (a VISA timeout)
lverror.is_warning(200010)      # True  (positive, undocumented: a warning by convention)
lverror.is_error(0)             # False (zero means success)
```

`explain(code)` returns the documented description or `None`. `describe(code)` returns an
`ErrorInfo` with the `code`, the `message` (if known), the `family` it falls in, and the
`is_error` / `is_warning` flags. `is_error(code)` and `is_warning(code)` are also available
on their own.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
