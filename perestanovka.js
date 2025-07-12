const perestanovka = (containerId, perfectWidth, initialColumnsNumber, params) => {
  if (!params) {
    const container = document.querySelector(`#${containerId}`);
    const items = [...document.querySelectorAll(`#${containerId} > div`)];

    container.style.position = 'relative';

    items.forEach(item => {
      item.style.position = 'absolute';
      item.style.transition = '0.5s';
    });

    params = {
      isInitialized: false,
      container,
      items,
      columnsNumber: initialColumnsNumber,
      itemsOrder: items.map((_, index) => index),
    };
  }

  const shuffleItemsOrder = () => {
    if (!params.isInitialized) {
      params.isInitialized = true;
      return;
    }

    const order = params.itemsOrder;

    for (let i = order.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [order[i], order[j]] = [order[j], order[i]];
    }
  };

  const resizeItems = () => {
    const containerWidth = params.container.clientWidth;
    const widthCoefficient = containerWidth / perfectWidth;

    params.columnsNumber = Math.round(widthCoefficient * initialColumnsNumber);

    params.items.forEach(item => {
      item.style.width = `calc(100% / ${params.columnsNumber})`;
    });
  };

  const locateItems = () => {
    let row = 0;
    let column = 0;
    let maxColumnHeight = 0;

    params.itemsOrder.forEach((itemIndex, index) => {
      const item = params.items[itemIndex];

      if (row === 0) {
        item.style.top = '0';
      } else {
        const upperItemIndex = params.itemsOrder[index - params.columnsNumber];
        const upperItem = params.items[upperItemIndex];

        item.style.top = `${parseInt(upperItem.style.top) + upperItem.clientHeight}px`;
      }

      const height = parseInt(item.style.top) + item.clientHeight;

      if (height > maxColumnHeight) maxColumnHeight = height;

      item.style.left = `calc(100% / ${params.columnsNumber} * ${column})`;
      column++;

      if (column === params.columnsNumber) {
        column = 0;
        row++;
      }
    });

    params.container.style.height = `${maxColumnHeight}px`;
  };

  resizeItems();
  setTimeout(locateItems, 500);

  window.onresize = () => {
    perestanovka(containerId, perfectWidth, initialColumnsNumber, params);
  };
};
