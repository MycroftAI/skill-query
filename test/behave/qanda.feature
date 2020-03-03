Feature: Question and Answer functionality

  Scenario Outline: user asks who someone is
    Given an english speaking user
     When the user says "<who is george church>"
     Then mycroft reply should contain "<church>"

  Examples: who questions
    | who is george church | church |
    | who is george church | church |
    | who are the foo fighters | foo |
    | who built the eiffel tower | sauvestre |
    | who wrote the book outliers | gladwell |
    | who discovered helium | janssen |

  Scenario Outline: user asks a what question
    Given an english speaking user
     When the user says "<what is metallurgy>"
     Then mycroft reply should contain "<metallurgy>"

  Examples: what questions
    | what is metallurgy | metallurgy |
    | what is metallurgy | metallurgy |
    | what is the melting point of aluminum | 660 |

  Scenario Outline: user asks when something is
    Given an english speaking user
     When the user says "<when was alexander the great born>"
     Then mycroft reply should contain "<356>"

  Examples: what questions
    | when was alexander the great born | 356 |
    | when was alexander the great born | 356 |
    | when will the sun die | billion |
    | when is the next leap year | leap |
    | when was the last ice age | glacial |

  Scenario Outline: user asks where something is
   Given an english speaking user
    When the user says "<where is morocco>"
    Then mycroft reply should contain "<africa>"

  Examples: what questions
    | where is morocco | africa |
    | where is morocco | africa |
    | where is saturn | saturn |
    | where is the smithsonian | washington |

  Scenario Outline: user asks a how question
    Given an english speaking user
     When the user says "<how tall is the eiffel tower>"
     Then mycroft reply should contain "<1063>"

  Examples: what questions
    | how tall is the eiffel tower | 1063 |
    | how tall is the eiffel tower | 1063 |
    | how far away is the moon | distance |
    | how far is it from vienna to berlin | vienna |


  @xfail
  Scenario Outline: user asks a question mycroft can't answer
    Given an english speaking user
     When the user says "<failing query>"
     Then mycroft resply should contain "<expected answer>"

  Examples: what questions
    | failing query | expected answer |
    | what is a timer | interval |
    | what is the drinking age in canada | 19 |
    | how hot is the sun | sun |
