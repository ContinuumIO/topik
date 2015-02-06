def test(verbose=False, junitfile=None, exit=False):
    """
    Runs the full into test suite, outputting
    the results of the tests to sys.stdout.
    This uses py.test to discover which tests to
    run, and runs tests in any 'tests' subdirectory
    within the into module.
    Parameters
    ----------
    verbose : int, optional
        Value 0 prints very little, 1 prints a little bit,
        and 2 prints the test names while testing.
    junitfile : string, optional
        If provided, writes the test results to an junit xml
        style xml file. This is useful for running the tests
        in a CI server such as Jenkins.
    exit : bool, optional
        If True, the function will call sys.exit with an
        error code after the tests are finished.
    """
    import os
    import sys
    import pytest

    args = []

    if verbose:
        args.append('--verbose')

    # Output an xunit file if requested
    if junitfile is not None:
        args.append('--junit-xml=%s' % junitfile)

    # Add all 'tests' subdirectories to the options
    rootdir = os.path.dirname(__file__)
    for root, dirs, files in os.walk(rootdir):
        if 'tests' in dirs:
            testsdir = os.path.join(root, 'tests')
            args.append(testsdir)
            print('Test dir: %s' % testsdir[len(rootdir) + 1:])

    # Ask pytest to do its thing
    error_code = pytest.main(args=args)
    if exit:
        return sys.exit(error_code)
    return error_code == 0
