<div align="center">
  <a href="https://koyeb.com">
    <img src="https://www.koyeb.com/static/images/icons/koyeb.svg" alt="Logo" width="80" height="80">
  </a>
  <h3 align="center">Koyeb Serverless Platform</h3>
  <p align="center">
    Deploy a MCP Server using Gradio on Koyeb
    <br />
    <a href="https://koyeb.com">Learn more about Koyeb</a>
    ·
    <a href="https://koyeb.com/docs">Explore the documentation</a>
    ·
    <a href="https://koyeb.com/tutorials">Discover our tutorials</a>
  </p>
</div>

## About Koyeb and the Gradio MCP Server example application

Koyeb is a developer-friendly serverless platform to deploy apps globally. No-ops, servers, or infrastructure management.
This repository contains an example MCP Server built with Gradio you can deploy on the Koyeb serverless platform.

This example application is designed to show how an MCP server can be deployed on Koyeb.

## Getting Started

Follow the steps below to deploy and run the MCP server on your Koyeb account.

### Requirements

You need a Koyeb account to successfully deploy and run this application. If you don't already have an account, you can sign-up for free [here](https://app.koyeb.com/auth/signup).

### Deploy using the Koyeb button

The fastest way to deploy the MCP server built with Gradio is to click the **Deploy to Koyeb** button below.

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=https://github.com/koyeb/example-mcp-server-gradio-postgresql&branch=main&instance_type=small&region=was&type=web&min_scale=0&max_scale=5&autoscaling_concurrent_requests=5&run_command=python+app.py)

Clicking on this button brings you to the Koyeb App creation page with everything pre-set to launch this application.

Note: This app requires a PostgreSQL database. You’ll need to create one separately using the Koyeb CLI and run the provided migration and population scripts.

📖 Check the tutorial for instructions on setting up the database with your dataset of choice.

## Contributing

If you have any questions, ideas or suggestions regarding this application sample, feel free to open an [issue](//github.com/koyeb/example-mcp-server-gradio-postgresql/issues) or fork this repository and open a [pull request](//github.com/koyeb/example-mcp-server-gradio-postgresql/pulls).

## Contact

[Koyeb](https://www.koyeb.com) - [@gokoyeb](https://twitter.com/gokoyeb) - [Slack](http://slack.koyeb.com/)
