#!/usr/bin/env bash
# Trigger an error if non-zero exit code is encountered
set -e

if [ "$CLOUD_DEV" = "true" ] && [ -f ".env.development" ]; then
  rm .env.development
fi

# Colors
CS='\033[1;36m' # Light Cyan
NC='\033[0m'    # No Color
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'

entrypoint="$(pwd)"

# Syncing dependencies
new="${entrypoint}"
old='/home'
files=( 'package.json' ) # Add 'package-lock.json' for a more strict verification

echo -e "${CS}Checking dependencies files diff${NC}"
for file in "${files[@]}"
do
    cur_file="File: '${file}'"
    echo "Checking ${cur_file}"
    if ! diff "${new}/${file}" "${old}/${file}" --side-by-side --suppress-common-lines
    then
        echo -e "${YELLOW} ${cur_file} has differences between image and latest, installing dependencies${NC}"

        # Installing in docker local
        cp "${new}"/package*.json "${old}"
        cd "${old}"
        npm install

        # Copying new package-lock.json to host folder
        cp "${old}"/package-lock.json "${new}"

        echo -e "${GREEN}Done. Your package-lock.json has updated${NC}"
        break
    else
        echo -e "${GREEN} ${cur_file} ok${NC}"
    fi
done


cd "${entrypoint}"

echo -e "${YELLOW}MYSQL service must be running!${NC}"

echo -e "${YELLOW}creating DB ${DATABASE_NAME} if not exists${NC}"
SERVICE_DB_NAME=$DATABASE_NAME
export DATABASE_NAME=mysql
npm run typeorm query "CREATE DATABASE IF NOT EXISTS $SERVICE_DB_NAME"
export DATABASE_NAME=$SERVICE_DB_NAME

# Auto migrations step
echo -e "${CS}Checking for new migrations${NC}"
migration_count_file="/home/migration_count.txt"
old_migration_count=$(cat "${migration_count_file}" || echo 0) 2>/dev/null
new_migration_count=$(ls migration 2>/dev/null | wc -l)

if [ "${new_migration_count}" -gt "${old_migration_count}" ]
then
  echo -e "${YELLOW}Found pending migrations, migrating...${NC}"
  echo "${new_migration_count}" > "${migration_count_file}"
  npm run build
  npm run db:migrate 2>/dev/null || \
    (
      echo -e "${YELLOW}You need to update your 'package.json' scrips to support 'db:migrate'!
        ${YELLOW}Falling back to manual migration.${NC}" \
      && npm run typeorm -- migration:run \
    )
elif [ "${new_migration_count}" -lt "${old_migration_count}" ]
then
  echo -e "${YELLOW}Your latest code has less migration then the code at build time (or last migration)...${NC}"
  echo -e "  -> ${YELLOW}Please verify that your migrations timeline has not been altered.${NC}"
  echo -e "  -> ${YELLOW}To remove this warning you can rebuild your image.${NC}"
else
  echo -e "${GREEN}No migrations pending${NC}"
fi


printf "\n"
echo -e "${GREEN}Starting development docker${NC}"
printf "\n\n\n\n\n\n\n\n"
npm run start:debug
