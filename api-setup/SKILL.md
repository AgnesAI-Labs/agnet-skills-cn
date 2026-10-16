---
name: api-setup
name_zh: API集成配置助手
description: Set up API integration with configuration and helper scripts
description_zh: >-
  让 API 接入更简单！通过配置文件和辅助脚本，帮助你完成新 API 的集成配置，梳理接口接入所需的参数与操作步骤，减少重复配置工作，让第三方服务更方便地接入现有项目。
category: development
category_name: Development
category_name_zh: 开发与代码
examples_zh:
  - 帮我接入这个 API，包括配置和调用示例
  - 为新的第三方服务建立 API 集成
  - 按规范补一份 API 接入说明
examples:
  - Set up this API with config and usage examples
  - Create an integration for a new third-party service
  - Write API setup docs following our conventions
author: agnes
version: '1.0'
tags:
  - api
  - integration
  - setup
installation_notes: >-
  This skill installs with supporting setup scripts and configuration templates
  from the Skills Marketplace in Agnes Code Desktop.
installation_notes_zh: 该技能从 Agnes Code 桌面端技能市场安装，包含配套的配置脚本与配置模板。
---

# API Setup

This skill helps you set up a new API integration with our standard configuration.

## Steps

1. Run `setup.sh <api-name>` to create the integration directory
2. Copy `templates/config.template.json` to your integration directory
3. Update the config with your API credentials
4. Test the connection

## Configuration

The config template includes:

- `api_key`: Your API key (get from the provider's dashboard)
- `endpoint`: API endpoint URL
- `timeout`: Request timeout in seconds (default: 30)

## Verification

After setup, verify:

- [ ] Config file is valid JSON
- [ ] API key is set and not a placeholder
- [ ] Test connection succeeds

## Troubleshooting

### Connection Timeout

If you experience connection timeouts:

1. Check your network connection
2. Verify the endpoint URL is correct
3. Increase the timeout value in config

### Authentication Errors

If you get 401/403 errors:

1. Verify your API key is correct
2. Check if the key has the required permissions
3. Ensure the key hasn't expired
