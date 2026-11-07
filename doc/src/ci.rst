
#######################################################################################################################
Test Automation Server
#######################################################################################################################

HDLRegression support development automation server tools such as Jenkins and GitLab. When using HDLRegression with an automation 
server the test runner script will need to utilize the statistical method ``get_num_fail_tests()`` in HDLRegression and 
exit with an exit code to trigger a PASS/FAIL test in the automation server. 

**Example code - returning the number of failing tests to the automation server:**

.. code-block:: python

  # run tests
  ret_code = hr.start()
  # exit with the return code from start()
  sys.exit(ret_code)


.. note::

  The automation server will indicate a passing test when the test runnner script returns '**0**' exit code,
  and ``start()`` will return '**0**' if all tests have passed and there are no compilation errors.


**Example of building HDLRegression package and running test script in Jenkins:**

.. image:: images/jenkins_ci.png
  :width: 750
  :name: Jenkins server
  :align: center