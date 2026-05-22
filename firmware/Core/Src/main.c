/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2026 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

#define DELAY 150
#define MASK_STM_TX 32
#define MASK_STM_RX 16
#define MASK_STM_SWDIO 8
#define MASK_STM_SWDSWO 4
#define MASK_STM_RESET 2
#define MASK_STM_BOOT0 1

uint32_t START_TX = 0;
uint32_t START_RX = 0;
uint32_t START_SWDIO = 0;
uint32_t START_SWDSWO = 0;
uint32_t START_RESET = 0;
uint32_t START_BOOT0 = 0;

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

#define PUTCHAR_PROTOTYPE int __io_putchar(int ch)

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

UART_HandleTypeDef huart1;

/* USER CODE BEGIN PV */
volatile uint8_t led_status = 0x00;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART1_UART_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

PUTCHAR_PROTOTYPE {
	HAL_UART_Transmit(&huart1, (uint8_t*) &ch, 1, 0xFFFF);
	return ch;
}

void HAL_GPIO_EXTI_Rising_Callback(uint16_t pin) {
	if (pin == STM_TX_Pin) {
		led_status |= MASK_STM_TX;
	}

	if (pin == STM_BOOT0_Pin) {
		led_status |= MASK_STM_BOOT0;
	}
}

void HAL_GPIO_EXTI_Falling_Callback(uint16_t pin) {
	if (pin == STM_RX_Pin) {
		led_status |= MASK_STM_RX;
	}
	if (pin == STM_SWDIO_Pin) {
		led_status |= MASK_STM_SWDIO;
	}
	if (pin == STM_SWDSWO_Pin) {
		led_status |= MASK_STM_SWDSWO;
	}
	if (pin == STM_RESET_Pin) {
		led_status |= MASK_STM_RESET;
	}
}

void leds_on() {
	uint8_t local = led_status;
	if (local == 0) {
		return;
	}
	led_status = 0;
	uint32_t now = HAL_GetTick() + DELAY;

	if (local & MASK_STM_RX) {
		START_RX = now;
		HAL_GPIO_WritePin(LED_STM_RX_GPIO_Port, LED_STM_RX_Pin, GPIO_PIN_SET);
	}
	if (local & MASK_STM_SWDIO) {
		START_SWDIO = now;
		HAL_GPIO_WritePin(LED_STM_SWDIO_GPIO_Port, LED_STM_SWDIO_Pin, GPIO_PIN_SET);
	}
	if (local & MASK_STM_SWDSWO) {
		START_SWDSWO = now;
		HAL_GPIO_WritePin(LED_STM_SWDSWO_GPIO_Port, LED_STM_SWDSWO_Pin, GPIO_PIN_SET);
	}
	if (local & MASK_STM_RESET) {
		START_RESET = now;
		HAL_GPIO_WritePin(LED_STM_RESET_GPIO_Port, LED_STM_RESET_Pin, GPIO_PIN_SET);
	}
	if (local & MASK_STM_BOOT0) {
		START_BOOT0 = now;
		HAL_GPIO_WritePin(LED_STM_BOOT0_GPIO_Port, LED_STM_BOOT0_Pin, GPIO_PIN_SET);
	}
}

void leds_off() {
	uint32_t now = HAL_GetTick();

	if (now > START_TX && HAL_GPIO_ReadPin(STM_TX_GPIO_Port, STM_TX_Pin) == 0) {
		HAL_GPIO_WritePin(LED_STM_TX_GPIO_Port, LED_STM_TX_Pin, GPIO_PIN_RESET);
	}
	if (now > START_RX && HAL_GPIO_ReadPin(STM_RX_GPIO_Port, STM_RX_Pin) != 0) {
		HAL_GPIO_WritePin(LED_STM_RX_GPIO_Port, LED_STM_RX_Pin, GPIO_PIN_RESET);
	}
	if (now > START_SWDIO && HAL_GPIO_ReadPin(STM_SWDIO_GPIO_Port, STM_SWDIO_Pin) != 0) {
		HAL_GPIO_WritePin(LED_STM_SWDIO_GPIO_Port, LED_STM_SWDIO_Pin, GPIO_PIN_RESET);
	}
	if (now > START_SWDSWO && HAL_GPIO_ReadPin(STM_SWDSWO_GPIO_Port, STM_SWDSWO_Pin) != 0) {
		HAL_GPIO_WritePin(LED_STM_SWDSWO_GPIO_Port, LED_STM_SWDSWO_Pin, GPIO_PIN_RESET);
	}
	if (now > START_RESET && HAL_GPIO_ReadPin(STM_RESET_GPIO_Port, STM_RESET_Pin) != 0) {
		HAL_GPIO_WritePin(LED_STM_RESET_GPIO_Port, LED_STM_RESET_Pin, GPIO_PIN_RESET);
	}
	if (now > START_BOOT0 && HAL_GPIO_ReadPin(STM_BOOT0_GPIO_Port, STM_BOOT0_Pin) == 0) {
		HAL_GPIO_WritePin(LED_STM_BOOT0_GPIO_Port, LED_STM_BOOT0_Pin, GPIO_PIN_RESET);
	}
}

void led_init() {
	leds_off();
	HAL_Delay(300);
	HAL_GPIO_WritePin(LED_STM_TX_GPIO_Port, LED_STM_TX_Pin, GPIO_PIN_SET);
	HAL_Delay(300);
	HAL_GPIO_WritePin(LED_STM_RX_GPIO_Port, LED_STM_RX_Pin, GPIO_PIN_SET);
	HAL_Delay(300);
	HAL_GPIO_WritePin(LED_STM_SWDIO_GPIO_Port, LED_STM_SWDIO_Pin, GPIO_PIN_SET);
	HAL_Delay(300);
	HAL_GPIO_WritePin(LED_STM_SWDSWO_GPIO_Port, LED_STM_SWDSWO_Pin, GPIO_PIN_SET);
	HAL_Delay(300);
	HAL_GPIO_WritePin(LED_STM_RESET_GPIO_Port, LED_STM_RESET_Pin, GPIO_PIN_SET);
	HAL_Delay(300);
	HAL_GPIO_WritePin(LED_STM_BOOT0_GPIO_Port, LED_STM_BOOT0_Pin, GPIO_PIN_SET);

	HAL_Delay(300);
	HAL_GPIO_WritePin(LED_STM_TX_GPIO_Port, LED_STM_TX_Pin, GPIO_PIN_RESET);
	HAL_Delay(300);
	HAL_GPIO_WritePin(LED_STM_RX_GPIO_Port, LED_STM_RX_Pin, GPIO_PIN_RESET);
	HAL_Delay(300);
	HAL_GPIO_WritePin(LED_STM_SWDIO_GPIO_Port, LED_STM_SWDIO_Pin, GPIO_PIN_RESET);
	HAL_Delay(300);
	HAL_GPIO_WritePin(LED_STM_SWDSWO_GPIO_Port, LED_STM_SWDSWO_Pin, GPIO_PIN_RESET);
	HAL_Delay(300);
	HAL_GPIO_WritePin(LED_STM_RESET_GPIO_Port, LED_STM_RESET_Pin, GPIO_PIN_RESET);
	HAL_Delay(300);
	HAL_GPIO_WritePin(LED_STM_BOOT0_GPIO_Port, LED_STM_BOOT0_Pin, GPIO_PIN_RESET);
	HAL_Delay(300);
}

/* USER CODE END 0 */

/**
 * @brief  The application entry point.
 * @retval int
 */
int main(void) {

	/* USER CODE BEGIN 1 */

	/* USER CODE END 1 */

	/* MCU Configuration--------------------------------------------------------*/

	/* Reset of all peripherals, Initializes the Flash interface and the Systick. */
	HAL_Init();

	/* USER CODE BEGIN Init */

	/* USER CODE END Init */

	/* Configure the system clock */
	SystemClock_Config();

	/* USER CODE BEGIN SysInit */

	/* USER CODE END SysInit */

	/* Initialize all configured peripherals */
	MX_GPIO_Init();
	MX_USART1_UART_Init();
	/* USER CODE BEGIN 2 */

	HAL_Delay(500);
	printf("\n\nSTYX32 started...\n");
	led_init();

	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */
	while (1) {
		leds_on();
		leds_off();
		/* USER CODE END WHILE */

		/* USER CODE BEGIN 3 */
	}
	/* USER CODE END 3 */
}

/**
 * @brief System Clock Configuration
 * @retval None
 */
void SystemClock_Config(void) {
	RCC_OscInitTypeDef RCC_OscInitStruct = { 0 };
	RCC_ClkInitTypeDef RCC_ClkInitStruct = { 0 };

	__HAL_FLASH_SET_LATENCY(FLASH_LATENCY_0);

	/** Initializes the RCC Oscillators according to the specified parameters
	 * in the RCC_OscInitTypeDef structure.
	 */
	RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
	RCC_OscInitStruct.HSIState = RCC_HSI_ON;
	RCC_OscInitStruct.HSIDiv = RCC_HSI_DIV4;
	RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
	if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
		Error_Handler();
	}

	/** Initializes the CPU, AHB and APB buses clocks
	 */
	RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_PCLK1;
	RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
	RCC_ClkInitStruct.SYSCLKDivider = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.AHBCLKDivider = RCC_HCLK_DIV1;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_APB1_DIV1;

	if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK) {
		Error_Handler();
	}
}

/**
 * @brief USART1 Initialization Function
 * @param None
 * @retval None
 */
static void MX_USART1_UART_Init(void) {

	/* USER CODE BEGIN USART1_Init 0 */

	/* USER CODE END USART1_Init 0 */

	/* USER CODE BEGIN USART1_Init 1 */

	/* USER CODE END USART1_Init 1 */
	huart1.Instance = USART1;
	huart1.Init.BaudRate = 115200;
	huart1.Init.WordLength = UART_WORDLENGTH_8B;
	huart1.Init.StopBits = UART_STOPBITS_1;
	huart1.Init.Parity = UART_PARITY_NONE;
	huart1.Init.Mode = UART_MODE_TX;
	huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
	huart1.Init.OverSampling = UART_OVERSAMPLING_16;
	huart1.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
	huart1.Init.ClockPrescaler = UART_PRESCALER_DIV1;
	huart1.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
	if (HAL_UART_Init(&huart1) != HAL_OK) {
		Error_Handler();
	}
	if (HAL_UARTEx_SetTxFifoThreshold(&huart1, UART_TXFIFO_THRESHOLD_1_8) != HAL_OK) {
		Error_Handler();
	}
	if (HAL_UARTEx_SetRxFifoThreshold(&huart1, UART_RXFIFO_THRESHOLD_1_8) != HAL_OK) {
		Error_Handler();
	}
	if (HAL_UARTEx_DisableFifoMode(&huart1) != HAL_OK) {
		Error_Handler();
	}
	/* USER CODE BEGIN USART1_Init 2 */

	/* USER CODE END USART1_Init 2 */

}

/**
 * @brief GPIO Initialization Function
 * @param None
 * @retval None
 */
static void MX_GPIO_Init(void) {
	GPIO_InitTypeDef GPIO_InitStruct = { 0 };
	/* USER CODE BEGIN MX_GPIO_Init_1 */

	/* USER CODE END MX_GPIO_Init_1 */

	/* GPIO Ports Clock Enable */
	__HAL_RCC_GPIOB_CLK_ENABLE();
	__HAL_RCC_GPIOC_CLK_ENABLE();
	__HAL_RCC_GPIOF_CLK_ENABLE();
	__HAL_RCC_GPIOA_CLK_ENABLE();

	/*Configure GPIO pin Output Level */
	HAL_GPIO_WritePin(GPIOA,
	LED_STM_BOOT0_Pin | LED_STM_RESET_Pin | LED_STM_SWDSWO_Pin | LED_STM_SWDIO_Pin | LED_STM_RX_Pin | LED_STM_TX_Pin,
			GPIO_PIN_RESET);

	/*Configure GPIO pin : PC15 */
	GPIO_InitStruct.Pin = GPIO_PIN_15;
	GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

	/*Configure GPIO pin : PF2 */
	GPIO_InitStruct.Pin = GPIO_PIN_2;
	GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(GPIOF, &GPIO_InitStruct);

	/*Configure GPIO pin : STM_BOOT0_Pin */
	GPIO_InitStruct.Pin = STM_BOOT0_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(STM_BOOT0_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pins : LED_STM_BOOT0_Pin LED_STM_RESET_Pin LED_STM_SWDSWO_Pin LED_STM_SWDIO_Pin
	 LED_STM_RX_Pin LED_STM_TX_Pin */
	GPIO_InitStruct.Pin = LED_STM_BOOT0_Pin | LED_STM_RESET_Pin | LED_STM_SWDSWO_Pin | LED_STM_SWDIO_Pin
			| LED_STM_RX_Pin | LED_STM_TX_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

	/*Configure GPIO pins : STM_RX_Pin STM_TX_Pin */
	GPIO_InitStruct.Pin = STM_RX_Pin | STM_TX_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
	GPIO_InitStruct.Pull = GPIO_PULLUP;
	HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

	/*Configure GPIO pins : STM_SWDSWO_Pin STM_SWDIO_Pin */
	GPIO_InitStruct.Pin = STM_SWDSWO_Pin | STM_SWDIO_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

	/*Configure GPIO pin : STM_RESET_Pin */
	GPIO_InitStruct.Pin = STM_RESET_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(STM_RESET_GPIO_Port, &GPIO_InitStruct);

	/* EXTI interrupt init*/
	HAL_NVIC_SetPriority(EXTI0_1_IRQn, 0, 0);
	HAL_NVIC_EnableIRQ(EXTI0_1_IRQn);

	HAL_NVIC_SetPriority(EXTI4_15_IRQn, 0, 0);
	HAL_NVIC_EnableIRQ(EXTI4_15_IRQn);

	/* USER CODE BEGIN MX_GPIO_Init_2 */

	/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
 * @brief  This function is executed in case of error occurrence.
 * @retval None
 */
void Error_Handler(void) {
	/* USER CODE BEGIN Error_Handler_Debug */
	/* User can add his own implementation to report the HAL error return state */
	__disable_irq();
	while (1) {
	}
	/* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
