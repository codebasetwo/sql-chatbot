# Business Copilot

Business Copilot is a Python-based analytics toolkit designed to streamline business intelligence workflows, database interactions, and memory management for data-driven applications. The project is modular, extensible, and includes utilities for working with PostgreSQL, business analytics, and prompt engineering.

## Features

- **Business Analytics Tools**: Utilities for data analysis, business logic, and workflow automation.
- **PostgreSQL Utilities**: Simplified database connections, queries, and management.
- **Memory Management**: In-memory data handling for efficient analytics pipelines.
- **Prompt Engineering**: Tools for building and managing prompts for LLMs or AI agents.
- **Jupyter Notebooks**: Example notebooks for scoping and database testing.

## Project Structure

```
src/
	business_copilot/
		biz_analytics/
			db_tools.py        # Database tools and helpers
			main.py            # Main analytics entry point
			memory.py          # In-memory data management
			pgres_utils.py     # PostgreSQL utilities
			prompts.py         # Prompt engineering utilities
			schemas.py         # Data schemas and models
			utils.py           # General utilities
		notebooks/
			1_scoping.ipynb    # Scoping and project planning
			2_postgres_test.ipynb # PostgreSQL integration tests
pyproject.toml           # Project metadata and dependencies
uv.lock                  # Dependency lock file
README.md                # Project documentation
```

## Installation

1. **Clone the repository:**
	 ```bash
	 git clone <your-repo-url>
	 cd business-copilot
	 ```

2. **Install dependencies:**
	 ```bash
	 pip install -r requirements.txt
	 ```
	 Or, if using Poetry or another tool, follow the instructions in `pyproject.toml`.

3. **(Optional) Set up your environment:**
	 - Configure your database credentials and environment variables as needed.

## Usage

- **Python Modules:**  
	Import and use the modules in your own scripts:
	```python
	from business_copilot.biz_analytics import db_tools, main, memory
	```

- **Jupyter Notebooks:**  
	Explore the `notebooks/` directory for example workflows and database integration tests.

- **Database Integration:**  
	Use `pgres_utils.py` and `db_tools.py` for connecting to and querying PostgreSQL databases.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or new features.

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please open an issue in the repository.
