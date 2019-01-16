Feature: Collect
  As a user, I want to use Yelp to collect information about businesses.

  Scenario: Collect information
    Given a research for "bike shops" and "Austin, TX"
    Then the generated file contains the collected data
