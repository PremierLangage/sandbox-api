# Changelog

### 1.1.0

* `Sandbox.check()` now return the size of the environment / file, 0 if not
    found. It should not break backward compatibility because of how int are
    evaluated as boolean.
* Added an `async` implementation of the api using the class `ASandbox`.
* `async` implementation depends on `aiohttp`.
* Drop support for Python 3.5 & 3.6

#### 1.0.1

* Update README.md

## 1.0.0

* Now compatible with Sandbox 3.0.0

#### 0.0.7

* Now use Github Action for testing and deployment to PyPI

#### 0.0.6

* Added method `Sandbox451`
* Added python 3.8 tp test matrix

#### 0.0.5

* Added method `check()` to `Sandbox` to check if an environment/file exists on the sandbox.


#### 0.0.4

* Added function `validate()` to check a config dict in `sandbox_api.utils`.


#### 0.0.3

* Added missing type hints `cpu` for `Sandbox`


#### 0.0.2

* Added type hints for `Sandbox`'s attributes.


#### 0.0.1

* Initial release
