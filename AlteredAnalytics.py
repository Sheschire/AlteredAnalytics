from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
import time
import re

PSEUDO = 'Sheschire'

def connect_to_bga(driver):
    # Connect to BGA
    driver.get("https://fr.boardgamearena.com/")
    driver.find_element(By.XPATH, '//a[@href="/account"]').click()

    loginField = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@name='email']"))
    )
    ActionChains(driver).move_to_element(loginField).click().send_keys("theo.lemesle42@gmail.com").perform()
    driver.find_element(By.XPATH, '//div[@class="bga-emailfield"]/following-sibling::div[1]').click()

    passwordField = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))
    )
    ActionChains(driver).move_to_element(passwordField).click().send_keys("fYP5gGFM").perform()
    driver.find_element(By.XPATH,
                        '/html/body/div[4]/div/div[2]/div/div/div[3]/div/div[2]/div/div[2]/div[2]/div/form/div[2]/div/div/a').click()

    time.sleep(2)
    driver.find_element(By.XPATH,
                        '/html/body/div[4]/div/div[2]/div/div/div[3]/div/div[2]/div/div[2]/div[3]/div[2]/div[3]/div[3]/div/div/a').click()

    time.sleep(5)

def navigate_to_stats(driver):
    driver.get("https://boardgamearena.com/gamestats")
    playerPage = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[5]/div[1]/div/div/div/div/div[1]/h2/a[1]'))
    )
    playerPage.click()
    current_url = driver.current_url
    parsed_url = urlparse(current_url)
    params = parse_qs(parsed_url.query)
    player_id = params.get('id', [None])[0]

    driver.get(f"https://boardgamearena.com/gamestats?player={player_id}&game_id=1909")

def create_stats(driver):
    def navigate_to_replay(row):
        cell = row.find_element(By.TAG_NAME, 'td')
        tableLink = cell.find_element(By.TAG_NAME, 'a')
        tableLink.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'reviewgame'))
        ).click()
        time.sleep(2)

    def get_my_role():
        xpath_expression = f"//*[contains(text(), '{PSEUDO} jouera avec')]"
        myRole = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_expression))
        ).text
        my_faction_and_character = re.findall(r'\b[A-Z][a-zA-ZÀ-ÖØ-öø-ÿ]*\b', myRole)
        my_faction = my_faction_and_character[1]
        my_character = my_faction_and_character[2]
        return my_faction, my_character

    def get_enemy_role():
        if win == 1:
            xpath_expression = f"//*[contains(text(), '{loser} jouera avec')]"
        else:
            xpath_expression = f"//*[contains(text(), '{winner} jouera avec')]"
        enemyRole = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_expression))
        ).text
        enemy_faction_and_character = re.findall(r'\b[A-Z][a-zA-ZÀ-ÖØ-öø-ÿ]*\b', enemyRole)
        enemy_faction = enemy_faction_and_character[1]
        enemy_character = enemy_faction_and_character[2]
        return enemy_faction, enemy_character

    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="gamelist_inner"]'))
    )
    rows = WebDriverWait(table, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
    )

    for row in rows:
        navigate_to_replay(row)

        gameResults = driver.find_elements(By.CLASS_NAME, 'score-entry')
        winner = gameResults[0].find_element(By.CLASS_NAME, 'name').find_element(By.TAG_NAME, 'a').text
        loser = gameResults[1].find_element(By.CLASS_NAME, 'name').find_element(By.TAG_NAME, 'a').text
        win = 1 if winner == PSEUDO else 0

        my_faction, my_character = get_my_role()
        print(f"I was {my_character} from {my_faction}")

        enemy_faction, enemy_character = get_enemy_role()
        print(f"Enemy was {enemy_character} from {enemy_faction}")
        driver.back()
        driver.back()
        time.sleep(50)


if __name__ == "__main__":
    # Launch Chrome
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options)
    wait = WebDriverWait(driver, 10)

    connect_to_bga(driver)
    navigate_to_stats(driver)
    create_stats(driver)

    # loadMore = driver.find_elements(By.XPATH, '//*[@id="see_more_tables"]')