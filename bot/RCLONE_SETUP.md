# Rclone Setup for Maximum Speed Uploads

## Installation

### Windows
1. Download rclone from: https://rclone.org/downloads/
2. Extract and add to PATH

### Verify Installation
```bash
rclone version
```

## Configure B2 Remote

Run this command and follow the prompts:

```bash
rclone config
```

### Configuration Steps:
1. Select **"New remote"**
2. Name it: `b2`
3. Storage type: `b2` (select option for Backblaze B2)
4. Account ID: `004f2f7daa17c500000000002`
5. Application Key: `K004ozruXnFNNq8cbFRxdYO1HhfJTSs`
6. Endpoint: `us` (default)
7. Hard delete: `false`
8. Leave other options as default

### Verify Configuration
```bash
rclone lsd b2:
```

You should see your buckets listed.

## Test Upload
```bash
rclone copy test.txt b2:social-feed-image --progress
```

## Speed Optimizations

The upload script uses these rclone flags for maximum speed:
- `--transfers=10` - Upload 10 files in parallel
- `--checkers=20` - Use 20 parallel checkers
- `--no-check-dest` - Skip destination checks (faster)
- `--fast-list` - Use fast directory listing

## Troubleshooting

If upload fails, check:
1. rclone is in PATH
2. Remote "b2" is configured
3. Check with: `rclone config show b2`




