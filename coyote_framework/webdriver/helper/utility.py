import datetime
import decimal


ID = 1
Class = 2
CSS = 3
Xpath = 4
LinkText = 5

def elementExists(driver, type, lookup):
    exists = True
    try:
        if type == ID:
            driver.find_element_by_id(lookup)
        elif type == Class:
            driver.find_element_by_class_name(lookup)
        elif type == CSS:
            driver.find_element_by_css_selector(lookup)
        elif type == LinkText:
            driver.find_element_by_link_text(lookup)
        elif type == Xpath:
            driver.find_element_by_Xpath(lookup)

    except:
        exists = False

    return exists


def date_by_adding_business_days(from_date, add_days):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += datetime.timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5: # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date

def assertEqual(actual, expected, msg=''):
    assert actual == expected, 'Actual value %s does not match expected %s: %s' % (actual, expected, msg)

def convertToEuro(amount, quantity, rate):
    euroQuantumAmount = decimal.Decimal(amount) / decimal.Decimal(rate)
    euro = roundUpToTwoDecimal(euroQuantumAmount) * quantity
    #print amount, '=>', euro
    return euro

def convertToDollar(amount, quantity, rate):
    dollarQuantumAmount = decimal.Decimal(amount) * decimal.Decimal(rate)
    dollar = roundUpToTwoDecimal(dollarQuantumAmount) * quantity
    return dollar

#defaults to no vat and usd exchange rate
def calculateTotalPrice(amount, exchangeRate = 1, vatRate = 0):

    convertPriceWithoutVat = roundUpToTwoDecimal(roundUpToTwoDecimal(decimal.Decimal(amount))/ decimal.Decimal(exchangeRate))
    convertVat = roundUpToTwoDecimal(roundUpToTwoDecimal(decimal.Decimal(amount * vatRate))/decimal.Decimal(exchangeRate))

    return roundUpToTwoDecimal(decimal.Decimal(convertPriceWithoutVat + convertVat))

def roundUpToTwoDecimal(amount):
    cents = decimal.Decimal('.01')
    return amount.quantize(cents, decimal.ROUND_HALF_UP)

def calculatePayPalEuroFee(amount):
    fee = roundUpToTwoDecimal(amount * decimal.Decimal(0.029)
                    + decimal.Decimal(0.35))
    return fee

def calculatePayPalUSDFee(amount):
    fee = roundUpToTwoDecimal(decimal.Decimal(amount) * decimal.Decimal(0.029) + decimal.Decimal(0.3))
    return fee
