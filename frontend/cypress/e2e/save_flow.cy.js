describe('Save & history flow', () => {
    it('should save a recommended name and show in history, then delete', () => {
        cy.visit('/');
        cy.get('input[placeholder="영어 이름 입력..."]').type('Bob');
        cy.contains('button', '추천').click();
        // wait result
        cy.get('.primary h2').should('be.visible');

        cy.contains('button', '💾 저장').click();

        // move to saved tab
        cy.contains('button', '내 이름 모아보기').click();

        cy.get('.saved-item').should('have.length', 1);

        // delete
        cy.get('.saved-item button').click();
        cy.get('.saved-item').should('have.length', 0);
    });
});
