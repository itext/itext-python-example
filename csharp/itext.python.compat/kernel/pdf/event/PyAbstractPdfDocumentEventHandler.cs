namespace iText.Kernel.Pdf.Event
{
    /// <summary>Base class for PDF document events handling based on the event type.</summary>
    /// <remarks>
    /// Base class for PDF document events handling based on the event type.
    /// <para />
    /// Handles
    /// <see cref="AbstractPdfDocumentEvent"/>
    /// event fired by
    /// <see cref="iText.Kernel.Pdf.PdfDocument.DispatchEvent(AbstractPdfDocumentEvent)"/>.
    /// Use
    /// <see cref="iText.Kernel.Pdf.PdfDocument.AddEventHandler(System.String, AbstractPdfDocumentEventHandler)"/>
    /// to register this handler for
    /// specific type of event.
    /// <para>
    /// This subclass makes <see cref="AbstractPdfDocumentEventHandler"/>
    /// protected methods public, so that they can be overridden under
    /// Python.NET.
    /// </para>
    /// </remarks>
    public abstract class PyAbstractPdfDocumentEventHandler : AbstractPdfDocumentEventHandler
    {
        protected sealed override void OnAcceptedEvent(AbstractPdfDocumentEvent @event)
        {
            _OnAcceptedEvent(@event);
        }

        /// <summary>Handles the accepted event.</summary>
        /// <param name="event">
        /// 
        /// <see cref="AbstractPdfDocumentEvent"/>
        /// to handle
        /// </param>
        public abstract void _OnAcceptedEvent(AbstractPdfDocumentEvent @event);
    }
}
