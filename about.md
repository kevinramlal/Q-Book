#  Price Discovery Process 
*Price discovery is the process in which a securities' price is determined through the interactions and mechanisms in a marketplace.* 

There are several important models in the price discovery process - each with varying levels of complexity as well as specific sets of assumptions. While these models may be a far cry from the complexity of real-world trading, studying the behavior of prices in these models help traders better understand the markets in which they trade. In this article I hope to outline several of the canonical models used through literature - and perhaps provide some insight as to why these models can be useful in real applications. 

### 1. Glosten Milgrom (1985)

We start with a simple framework, as follows:

1. There is a single security that can take on one of two values $V_H$ or $V_L$ where $V_H > V_L$.
2. You are the market-maker and you see order arrivals, one at time. 
3. There are two types of traders placing these orders, an **informed trader** who knows what the true value of the security, and a **liqudity trader** who has no knowledge of the true value.
4. The probability that any given order comes from an informed trader 