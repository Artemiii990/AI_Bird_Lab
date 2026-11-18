// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test} from "forge-std/Test.sol";
import {BirdSubscription} from "../BirdSubscription.sol";

contract BirdSubscriptionTest is Test {
    BirdSubscription public sub;
    address public user = makeAddr("user");

    function setUp() public {
        sub = new BirdSubscription();
        vm.deal(user, 1 ether); // Выдаём тестовому пользователю 1 ETH
    }

    // 1. По умолчанию у нового пользователя нет подписки
    function test_DefaultNotSubscribed() public view {
        assertFalse(sub.isSubscribed(user));
    }

    // 2. Успешная покупка подписки за 0.001 ETH
    function test_SubscribeSuccess() public {
        vm.prank(user); // Следующий вызов пойдёт от имени user
        sub.subscribe{value: 0.001 ether}();

        assertTrue(sub.isSubscribed(user));
    }

    // 3. Ошибка при попытке купить подписку дешевле 0.001 ETH
    function test_RevertWhen_InsufficientPayment() public {
        vm.prank(user);
        vm.expectRevert(); // Ожидаем, что транзакция отклонится
        sub.subscribe{value: 0.0001 ether}();
    }
}
