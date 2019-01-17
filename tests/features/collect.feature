Feature: Collect
  As a user, I want to use Yelper to collect information about
  businesses.

  Scenario: Collect information
    Given the user wants to store the results in a CSV file
    And the user research for "bike shops" in "Austin, TX"
    Then the generated file contains the collected data
