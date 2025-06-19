describe('Korean name recommendation flow', () => {
    it('should generate korean name candidates for valid english name', () => {
        cy.visit('/');
        cy.get('input[placeholder="영어 이름 입력..."]').type('Alice');
        cy.contains('button', '추천').click();

        // 기본 추천 결과 노출 확인
        cy.get('.primary h2').should('be.visible');
        cy.get('.others .other-item').should('have.length.at.least', 1);
    });

    it('should show validation error for invalid input', () => {
        cy.visit('/');
        cy.get('input[placeholder="영어 이름 입력..."]').type('123@@');
        cy.contains('button', '추천').should('be.disabled');
    });
});
