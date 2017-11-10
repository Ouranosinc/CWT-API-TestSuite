TEST_PATH=./


test:
  py.test --verbose --color=yes $(TEST_PATH)