API Documentation is maintained by Swagger UI
You can access it by launching the server in localhost:5000 and simply access the root folder.

Documentation Endpoint
localhost:5000/



``` Swagger.json
{
    "swagger": "2.0",
    "basePath": "/",
    "paths": {
        "/categories/": {
            "parameters": [
                {
                    "name": "X-Fields",
                    "in": "header",
                    "type": "string",
                    "format": "mask",
                    "description": "An optional fields mask"
                }
            ],
            "get": {
                "responses": {
                    "200": {
                        "description": "Success",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/category_list_model"
                            }
                        }
                    }
                },
                "summary": "List all categories",
                "operationId": "list_categories",
                "tags": [
                    "categories"
                ]
            }
        },
        "/questions/": {
            "post": {
                "responses": {
                    "200": {
                        "description": "Success",
                        "schema": {
                            "$ref": "#/definitions/question"
                        }
                    }
                },
                "summary": "Create a new question",
                "description": "Ensure that the difficulty and categories are a valid positive integer",
                "operationId": "post_question",
                "parameters": [
                    {
                        "name": "payload",
                        "required": true,
                        "in": "body",
                        "schema": {
                            "$ref": "#/definitions/question"
                        }
                    },
                    {
                        "name": "X-Fields",
                        "in": "header",
                        "type": "string",
                        "format": "mask",
                        "description": "An optional fields mask"
                    }
                ],
                "tags": [
                    "questions"
                ]
            },
            "get": {
                "responses": {
                    "200": {
                        "description": "Success",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/question_list"
                            }
                        }
                    }
                },
                "summary": "List all questions",
                "operationId": "list_questions",
                "parameters": [
                    {
                        "description": "page number. Each page contains 10 questions",
                        "name": "page",
                        "type": "string",
                        "in": "query"
                    },
                    {
                        "name": "X-Fields",
                        "in": "header",
                        "type": "string",
                        "format": "mask",
                        "description": "An optional fields mask"
                    }
                ],
                "tags": [
                    "questions"
                ]
            }
        },
        "/questions/filter": {
            "get": {
                "responses": {
                    "200": {
                        "description": "Success",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/search_result_model"
                            }
                        }
                    }
                },
                "summary": "List all questions",
                "operationId": "filter question by category",
                "parameters": [
                    {
                        "description": "category unique identifier. You can get the list of categories by making GET request to the category resource endpoint",
                        "name": "category",
                        "type": "string",
                        "in": "query"
                    },
                    {
                        "name": "X-Fields",
                        "in": "header",
                        "type": "string",
                        "format": "mask",
                        "description": "An optional fields mask"
                    }
                ],
                "tags": [
                    "questions"
                ]
            }
        },
        "/questions/search/": {
            "post": {
                "responses": {
                    "200": {
                        "description": "Success",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/search_result_model"
                            }
                        }
                    }
                },
                "summary": "Search for question based on term all questions",
                "operationId": "search_questions",
                "parameters": [
                    {
                        "name": "payload",
                        "required": true,
                        "in": "body",
                        "schema": {
                            "$ref": "#/definitions/search_model"
                        }
                    },
                    {
                        "name": "X-Fields",
                        "in": "header",
                        "type": "string",
                        "format": "mask",
                        "description": "An optional fields mask"
                    }
                ],
                "tags": [
                    "questions"
                ]
            }
        },
        "/questions/{question_id}": {
            "parameters": [
                {
                    "name": "question_id",
                    "in": "path",
                    "required": true,
                    "type": "integer"
                }
            ],
            "delete": {
                "responses": {
                    "200": {
                        "description": "Success"
                    }
                },
                "summary": "Delete questions by Id",
                "operationId": "delete_question",
                "tags": [
                    "questions"
                ]
            },
            "get": {
                "responses": {
                    "200": {
                        "description": "Success",
                        "schema": {
                            "$ref": "#/definitions/question"
                        }
                    }
                },
                "summary": "Get questions by Id",
                "operationId": "get_question",
                "parameters": [
                    {
                        "name": "X-Fields",
                        "in": "header",
                        "type": "string",
                        "format": "mask",
                        "description": "An optional fields mask"
                    }
                ],
                "tags": [
                    "questions"
                ]
            }
        },
        "/quizzes/": {
            "post": {
                "responses": {
                    "200": {
                        "description": "Success"
                    }
                },
                "summary": "get a random question",
                "operationId": "post_question_random",
                "parameters": [
                    {
                        "name": "payload",
                        "required": true,
                        "in": "body",
                        "schema": {
                            "$ref": "#/definitions/quizz_model"
                        }
                    }
                ],
                "tags": [
                    "quizzes"
                ]
            }
        }
    },
    "info": {
        "title": "Trivia API",
        "version": 1.0,
        "description": "API for Udacity trivia application"
    },
    "produces": [
        "application/json"
    ],
    "consumes": [
        "application/json"
    ],
    "tags": [
        {
            "name": "categories",
            "description": "Category operations"
        },
        {
            "name": "questions",
            "description": "Question operations"
        },
        {
            "name": "quizzes",
            "description": "Quizzes operations"
        }
    ],
    "definitions": {
        "category_list_model": {
            "properties": {
                "questions": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/category_model"
                    }
                },
                "count": {
                    "type": "integer",
                    "description": "Total number of questions available",
                    "readOnly": true
                }
            },
            "type": "object"
        },
        "category_model": {
            "properties": {
                "*": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "string"
                    }
                }
            },
            "type": "object"
        },
        "question": {
            "required": [
                "answer",
                "category",
                "difficulty",
                "question"
            ],
            "properties": {
                "id": {
                    "type": "integer",
                    "description": "The question unique identifier",
                    "readOnly": true
                },
                "question": {
                    "type": "string",
                    "description": "The question detail"
                },
                "answer": {
                    "type": "string",
                    "description": "The question answer"
                },
                "difficulty": {
                    "type": "integer",
                    "description": "The question difficulty",
                    "default": 1
                },
                "category": {
                    "type": "integer",
                    "description": "The question category",
                    "default": 1
                }
            },
            "type": "object"
        },
        "question_list": {
            "properties": {
                "total_questions": {
                    "type": "integer",
                    "description": "Total number of questions available",
                    "readOnly": true
                },
                "page": {
                    "type": "integer",
                    "description": "Page number. Each page contains 10 questions ",
                    "default": 1
                },
                "questions": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/question"
                    }
                },
                "categories": {
                    "$ref": "#/definitions/category_model"
                },
                "current_category": {
                    "type": "integer"
                }
            },
            "type": "object"
        },
        "search_model": {
            "required": [
                "searchTerm"
            ],
            "properties": {
                "searchTerm": {
                    "type": "string",
                    "description": "Search term"
                }
            },
            "type": "object"
        },
        "search_result_model": {
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "Number of questions found in the search",
                    "readOnly": true
                },
                "questions": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/question"
                    }
                }
            },
            "type": "object"
        },
        "quizz_model": {
            "required": [
                "quiz_category"
            ],
            "properties": {
                "quiz_category": {
                    "$ref": "#/definitions/quizz_category_model"
                },
                "previous_questions": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/question"
                    }
                }
            },
            "type": "object"
        },
        "quizz_category_model": {
            "required": [
                "id"
            ],
            "properties": {
                "id": {
                    "type": "integer",
                    "description": "Category id. 0 means all category"
                }
            },
            "type": "object"
        }
    },
    "responses": {
        "ParseError": {
            "description": "When a mask can't be parsed"
        },
        "MaskError": {
            "description": "When any error occurs on mask"
        },
        "ValueError": {
            "description": "Return a custom message and 422 status code"
        }
    }
}
```