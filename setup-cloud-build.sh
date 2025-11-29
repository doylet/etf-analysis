#!/bin/bash

# Cloud Build Trigger Setup Script
# Creates a GitHub-triggered Cloud Build pipeline

# Configuration
PROJECT_ID="conda-portfolio-dashboard"
REPO_OWNER="doylet"
REPO_NAME="etf-analysis"
TRIGGER_NAME="etf-analysis-deploy"
BRANCH_PATTERN="^master$"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Setting up Cloud Build Trigger${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set the project
echo -e "${BLUE}Setting GCP project...${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo -e "${BLUE}Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Grant Cloud Build permissions
echo -e "${BLUE}Granting Cloud Build service account permissions...${NC}"
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/run.admin" \
    --condition=None

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None

echo -e "${YELLOW}⚠️  Manual Step Required:${NC}"
echo -e "${YELLOW}You need to connect your GitHub repository to Cloud Build:${NC}"
echo ""
echo "1. Go to: https://console.cloud.google.com/cloud-build/triggers/connect?project=${PROJECT_ID}"
echo "2. Select 'GitHub' as the source"
echo "3. Authenticate with GitHub"
echo "4. Select repository: ${REPO_OWNER}/${REPO_NAME}"
echo "5. Click 'Connect'"
echo ""
echo -e "${BLUE}After connecting, press Enter to create the trigger...${NC}"
read -p ""

# Create the Cloud Build trigger
echo -e "${BLUE}Creating Cloud Build trigger...${NC}"
gcloud builds triggers create github \
    --name="${TRIGGER_NAME}" \
    --repo-name="${REPO_NAME}" \
    --repo-owner="${REPO_OWNER}" \
    --branch-pattern="${BRANCH_PATTERN}" \
    --build-config="cloudbuild.yaml" \
    --description="Auto-deploy ETF Analysis Dashboard on push to master"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Cloud Build trigger created successfully!${NC}"
    echo ""
    echo -e "${GREEN}Trigger Details:${NC}"
    echo "  Name: ${TRIGGER_NAME}"
    echo "  Repository: ${REPO_OWNER}/${REPO_NAME}"
    echo "  Branch: master"
    echo "  Build Config: cloudbuild.yaml"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "  1. Push changes to master branch"
    echo "  2. Cloud Build will automatically build and deploy"
    echo "  3. Monitor builds at: https://console.cloud.google.com/cloud-build/builds?project=${PROJECT_ID}"
else
    echo -e "${RED}❌ Failed to create trigger${NC}"
    echo -e "${YELLOW}Make sure you've connected the GitHub repository first${NC}"
    exit 1
fi
