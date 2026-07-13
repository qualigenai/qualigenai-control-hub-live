\# Architecture



\## High-Level Flow



```text

Systems Under Test

&#x20;   |

&#x20;   |-- Hybrid RAG v1.5

&#x20;   |-- Srisailam WhatsApp Bot

&#x20;   |-- Multi-Agent QA System

&#x20;   |

&#x20;   v

Golden Test Dataset

&#x20;   |

&#x20;   v

AI Test Runner

&#x20;   |

&#x20;   v

API Connector

&#x20;   |

&#x20;   v

AI Response

&#x20;   |

&#x20;   v

Evaluation Engine

&#x20;   |

&#x20;   |-- Factual Correctness

&#x20;   |-- Context Grounding

&#x20;   |-- Citation Validation

&#x20;   |-- Retrieval Validation

&#x20;   |-- Prompt Injection Testing

&#x20;   |

&#x20;   v

Risk Scoring

&#x20;   |

&#x20;   v

JSON / HTML Reports

&#x20;   |

&#x20;   v

Dashboard + CI/CD Quality Gate

MVP Architecture

golden_dataset.json
        |
        v
run_tests.py
        |
        v
RAG v1.5 API
        |
        v
Basic response validation
        |
        v
reports/json/latest_report.json

