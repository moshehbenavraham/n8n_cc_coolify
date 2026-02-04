#!/bin/bash
# Batch upgrade node typeVersions across all workflows
# Usage: ./upgrade_node_versions.sh [preview|apply] [workflow_id|all]

# Extract API key directly from .env file
N8N_API_KEY=$(grep "^N8N_API_KEY=" /home/aiwithapex/n8n_cc_coolify/.env | cut -d= -f2-)
export N8N_API_KEY

MODE="${1:-preview}"
TARGET="${2:-all}"
API_URL="http://localhost:5678"

# Known latest typeVersions (update as needed)
declare -A LATEST_VERSIONS=(
    # Core nodes
    ["n8n-nodes-base.httpRequest"]="4.2"
    ["n8n-nodes-base.set"]="3.4"
    ["n8n-nodes-base.if"]="2.2"
    ["n8n-nodes-base.switch"]="3.2"
    ["n8n-nodes-base.code"]="2"
    ["n8n-nodes-base.merge"]="3.1"
    ["n8n-nodes-base.splitInBatches"]="3"
    ["n8n-nodes-base.aggregate"]="1.1"
    ["n8n-nodes-base.filter"]="2.2"
    ["n8n-nodes-base.itemLists"]="3.1"
    ["n8n-nodes-base.splitOut"]="1.1"

    # Triggers
    ["n8n-nodes-base.webhook"]="2.1"
    ["n8n-nodes-base.formTrigger"]="2.2"
    ["n8n-nodes-base.scheduleTrigger"]="1.2"

    # Communication
    ["n8n-nodes-base.telegram"]="1.2"
    ["n8n-nodes-base.telegramTrigger"]="1.2"
    ["n8n-nodes-base.slack"]="2.2"
    ["n8n-nodes-base.gmail"]="2.1"

    # AI/LangChain nodes
    ["@n8n/n8n-nodes-langchain.agent"]="2"
    ["@n8n/n8n-nodes-langchain.lmChatOpenAi"]="1.2"
    ["@n8n/n8n-nodes-langchain.openAi"]="1.8"
    ["@n8n/n8n-nodes-langchain.memoryBufferWindow"]="1.3"
    ["@n8n/n8n-nodes-langchain.toolWorkflow"]="2.2"

    # Storage/Database
    ["n8n-nodes-base.googleSheets"]="4.5"
    ["n8n-nodes-base.googleDrive"]="3.2"
    ["n8n-nodes-base.postgres"]="2.5"
    ["n8n-nodes-base.mysql"]="2.4"
    ["n8n-nodes-base.airtable"]="2.1"
    ["n8n-nodes-base.notion"]="2.2"

    # Other common nodes
    ["n8n-nodes-base.executeWorkflow"]="1.2"
    ["n8n-nodes-base.respondToWebhook"]="1.1"
    ["n8n-nodes-base.dateTime"]="2.2"
    ["n8n-nodes-base.html"]="1.2"
)

echo "Node Version Upgrade Tool"
echo "Mode: $MODE | Target: $TARGET"
echo "========================="

# Get workflow IDs
if [ "$TARGET" = "all" ]; then
    # Fetch all workflow IDs first
    echo "Fetching workflow list..."
    WF_IDS=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$API_URL/api/v1/workflows?limit=250" | jq -r '.data[].id')

    # Get next page if exists
    CURSOR=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$API_URL/api/v1/workflows?limit=250" | jq -r '.nextCursor // empty')
    while [ -n "$CURSOR" ]; do
        WF_IDS="$WF_IDS $(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$API_URL/api/v1/workflows?limit=250&cursor=$CURSOR" | jq -r '.data[].id')"
        CURSOR=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$API_URL/api/v1/workflows?limit=250&cursor=$CURSOR" | jq -r '.nextCursor // empty')
    done
else
    WF_IDS="$TARGET"
fi

TOTAL=0
UPGRADED=0
TOTAL_NODES_TO_UPGRADE=0

for wf_id in $WF_IDS; do
    ((TOTAL++))

    # Fetch workflow
    WF_DATA=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$API_URL/api/v1/workflows/$wf_id")
    WF_NAME=$(echo "$WF_DATA" | jq -r '.name // "Unknown"')

    echo ""
    echo "[$TOTAL] $WF_NAME"

    # Find nodes needing upgrade
    UPGRADE_COUNT=0
    NODES_TO_UPGRADE=()

    while IFS=$'\t' read -r node_name node_type current_ver; do
        [ -z "$node_type" ] && continue

        latest_ver="${LATEST_VERSIONS[$node_type]:-}"
        [ -z "$latest_ver" ] && continue

        # Compare versions
        if awk "BEGIN {exit !($current_ver < $latest_ver)}" 2>/dev/null; then
            echo "    ↑ $node_name: v$current_ver → v$latest_ver"
            ((UPGRADE_COUNT++))
            ((TOTAL_NODES_TO_UPGRADE++))

            if [ "$MODE" = "apply" ]; then
                NODES_TO_UPGRADE+=("$node_name|$latest_ver")
            fi
        fi
    done < <(echo "$WF_DATA" | jq -r '.nodes[] | "\(.name)\t\(.type)\t\(.typeVersion)"')

    if [ $UPGRADE_COUNT -eq 0 ]; then
        echo "    ✓ All nodes current"
    elif [ "$MODE" = "apply" ]; then
        # Build JSON object mapping node names to new versions
        UPGRADES_JSON="{"
        FIRST=true
        for node_info in "${NODES_TO_UPGRADE[@]}"; do
            node_name="${node_info%%|*}"
            new_ver="${node_info##*|}"
            if [ "$FIRST" = true ]; then
                UPGRADES_JSON+="$(printf '%s' "$node_name" | jq -Rs .):$new_ver"
                FIRST=false
            else
                UPGRADES_JSON+=",$(printf '%s' "$node_name" | jq -Rs .):$new_ver"
            fi
        done
        UPGRADES_JSON+="}"

        # Apply updates using jq with the upgrades map
        # Also filter to only include properties accepted by PUT
        UPDATED_WF=$(echo "$WF_DATA" | jq --argjson upgrades "$UPGRADES_JSON" '
            {
                name: .name,
                nodes: [.nodes[] |
                    if $upgrades[.name] then .typeVersion = $upgrades[.name]
                    else . end
                ],
                connections: .connections,
                settings: .settings,
                staticData: .staticData
            } | with_entries(select(.value != null))')

        # PUT the full updated workflow
        RESULT=$(curl -s -X PUT \
            -H "X-N8N-API-KEY: $N8N_API_KEY" \
            -H "Content-Type: application/json" \
            -d "$UPDATED_WF" \
            "$API_URL/api/v1/workflows/$wf_id")

        if echo "$RESULT" | jq -e '.id' > /dev/null 2>&1; then
            echo "    ✓ Applied $UPGRADE_COUNT upgrades"
            ((UPGRADED++))
        else
            echo "    ✗ Error: $(echo "$RESULT" | jq -r '.message // "Unknown"')"
        fi
    fi
done

echo ""
echo "========================="
echo "Processed: $TOTAL workflows"
echo "Nodes to upgrade: $TOTAL_NODES_TO_UPGRADE"
[ "$MODE" = "preview" ] && echo ""
[ "$MODE" = "preview" ] && echo "Run with 'apply' to apply upgrades:"
[ "$MODE" = "preview" ] && echo "  ./upgrade_node_versions.sh apply [workflow_id|all]"
