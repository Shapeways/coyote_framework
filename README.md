# Coyote Framework

The Coyote Framework is a framework for functional testing.  Leveraging both Selenium and Python Requests,
it delivers repeatable, reliable, and easy to change tests, reducing downward pressure on both development and
testing.

More docs, including examples, will be coming up next.

# Example Application

We've dropped an example of how you might implement an application in the /example directory.  In there, you'll
find two folders: example_app and example_tests.  The example app demonstrates how you can implement page objects
and locators to instrument a page, in this case http://shapeways.github.io.  There's also a demonstration of how
to use the configuration infrastructure, which uses pythons ConfigParser.  The example tests directory are tests
you would write to test your application.  An important note: you need to provide the test framework with the 
location of the example.cfg file via the TEST_RUN_SETTING_HOST environment variable.  

There are two methods of using the TEST_RUN_SETTING_HOST variable.

1. Simply point it to the absolute path of your config file.
```
TEST_RUN_SETTING_CONFIG=/path/to/coyote_framework/example/example_app/config/example.cfg
```
2. A config string such as `TEST_RUN_SETTING_CONFIG="browser.headless,scripts.no_ssh"` will read paths:
```
<project_root>/config/browser/headless.cfg
<project_root>/config/scripts/no_ssh.cfg
```
##To run the example:

Install Firefox 31 From https://ftp.mozilla.org/pub/firefox/releases/31.8.0esr/ to `/usr/bin/firefox`

Install nose `pip install nose`

```
cd example
TEST_RUN_SETTING_CONFIG=example_app/config/example.cfg python -m nose
```
